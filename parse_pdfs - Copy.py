#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script showing how to select only text that is contained in a given rectangle
on a page.

We use the page method 'getTextWords()' which delivers a list of all words.
Every item contains the word's rectangle (given by its coordinates, not as a
fitz.Rect in this case).
From this list we subselect words positioned in the given rectangle (or are at
least partially contained).
We sort this sublist by ascending y-ccordinate, and then by ascending x value.
Each original line of the rectangle is then reconstructed using the itertools
'groupby' function.

Remarks
-------
1. The script puts words in the same line, if the y1 value of their bbox are
   *exactly* equal. Allowing some tolerance here is imaginable, e.g. by
   taking the fitz.IRect of the word rectangles instead.

2. Reconstructed lines will contain words with exactly one space between them.
   So any original multiple spaces will be ignored.
"""
from operator import itemgetter 
from itertools import groupby
import fitz
import os
import re
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, "pt-BR")


def to_money(str_money):
    amount = re.findall(r"(?:[1-9]\d{0,2}(?:\.\d{3})*|0)(?:,\d{1,2})", str_money)[0]
    signal = re.findall(r"(?:[CD]{1})", str_money)[0]
    if signal == "D": 
        money = -locale.atof(amount)
    else:
        money = locale.atof(amount)
    return money


# Definir Orquestrador:
# Abrir PDF
# Processar páginas
# Ver quantidades de Notas de Corretagem por arquivo




class NotaCorretagem:
    def __init__(self, date = None, brokerage_note=None, operation_value=None, nc_value=None, account = None):
        self.date = date
        self.brokerage_note = brokerage_note
        self.operation_value = operation_value
        self.nc_value = nc_value
        self.account = account



# some_file = os.path.join(my_files, "59448-20140711-NC5311691.pdf")
# some_file = os.path.join(my_files, "59448-20140717-NC5325064.pdf")
# some_file = os.path.join(my_files, "59448-20121207-NC3819768.pdf")
class Document:
    def __init__(self, some_file):
        self.file = some_file
        self.pages = []
        self.doc = None
        self.num_of_pages = None
        self.words = []
        self.ncs_in_file = []
        self.nc_quantity = 0
        self.date = None
        self.fomatedDate = None
        self.account = None
        self.financial_resume = {}
        self.transactions = []
        self.negotiations = []
        self.main()
    
    def main(self):

        self.process_file()
        self.get_tradings_ids()
        self.get_account()
        self.get_financial_resume()
        # self.get_transactions()
        self.get_transactions_for_options()

        self.doc.close()

    def process_file(self):
        print("Processando:", self.file)
        
        doc = fitz.open(self.file)     # any supported document type
        self.num_of_pages = doc.pageCount
        self.doc = doc
        word = ""
        for pno in range(0, self.num_of_pages):
            
            # print("Processando página:", pno)
            page = doc[pno]                    # we want text from this page
            self.pages.append(page)
            """
            Get all words on page in a list of lists. Each word is represented by:
            [x0, y0, x1, y1, word, bno, lno, wno]
            The first 4 entries are the word's rectangle coordinates, the last 3 are just
            technical info (block number, line number, word number).
            """
            word = page.getTextWords()
            self.words.append(word)
        

    def get_tradings_ids(self):
        # Return 'Data pregão' and 'Nota de Corretagem Nº'
        nc_quantity = 0
        rl1, rl2 = None, None
        ncs_in_file = self.ncs_in_file
        # We subselect from above list.
        for pno, page in enumerate(self.pages):
            rl1 = page.searchFor("Data pregão:")
            rl2 = page.searchFor("C.I")

            if rl1:
                ## Opening new NotaCorretagem
                brokerage_note = {}
                trading_floor = []
                txt = ""
                rect = rl1[0] | rl2[0]
                
                mywords = [w for w in self.words[pno] if fitz.Rect(w[:4]).intersects(rect)]
                mywords.sort(key = itemgetter(3, 0))
                group = groupby(mywords, key = itemgetter(3))
                for y1, gwords in group:
                    line = [w[4] for w in gwords]
                    trading_floor.append(line)
                    txt += " ".join(line)
                # If there are more than one Nota de Corretagem in the file:
                ncs_in_file.append(brokerage_note)
                note_id = [item for sublist in trading_floor for item in sublist if item.isnumeric()][0]
                
                ncs_in_file[nc_quantity]["Data"] = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", txt)[0]
                self.date = ncs_in_file[nc_quantity]["Data"]
                ncs_in_file[nc_quantity]["Nota"] = note_id 
                split_date = ncs_in_file[nc_quantity]["Data"].split("/")
                ncs_in_file[nc_quantity]["FormatoData"] = split_date[-1]+split_date[-2]+ split_date[-3]
                self.formatedDate = ncs_in_file[nc_quantity]["FormatoData"]
                self.account = self.get_account()
                nc_quantity += 1

        self.nc_quantity = nc_quantity
        self.ncs_in_file = ncs_in_file
        self.tradings_ids = [nc["Nota"] for nc in self.ncs_in_file]
        return self.ncs_in_file

    def get_account(self):
        # Get account from the first page
        page = self.pages[0]  
        words = self.words
        ncs_in_file = self.ncs_in_file
        rl1 = page.searchFor("Conta XP")
        rl2 = [(601,842),(0,0)]
        rect = rl1[0] | rl2[0]
        account_code = []
        for wd in words:
            mywords = [w for w in wd if fitz.Rect(w[:4]).intersects(rect)]
            mywords.sort(key = itemgetter(3, 0))
            group = groupby(mywords, key = itemgetter(3))
            for y1, gwords in group:
                info = " ".join(w[4] for w in gwords)
                account_code.append(info)
            for nc in range(0, self.nc_quantity):
                ncs_in_file[nc]["CodigoCliente"] = account_code[0]
        self.account = account_code[0]
        return self.account
            
    def get_transactions(self):
        transactions = None
        negotiations = []
        headers = ["Q Negociação", "C/V", "Prazo", "Obs", "Quantidade", "Preço/Ajuste", "Valor/Ajuste", "D/C"]
        # 5-SOMA C VIS 2 1.855,00 3.710,00 D
        for pno, page in enumerate(self.pages):

            ##### FIRST TYPE: Regular BOVESPA Transaction (Stocks and REITs)
            ### Get transactions for ações e fii:
            rl1 = page.searchFor("Bovespa - Depósito / Vista") 
            rl2 = page.searchFor("Resumo dos Negócios")       # rect list two
            if rl1 and rl2:
                # From the two search itens, we start from far left to far right.
                rl1 = [fitz.Rect(0,rl1[0].y0,601,rl1[0].y1)]
                rl2 = [fitz.Rect(0,rl2[0].y0,601,rl2[0].y1)]
                
                rect = rl1[0] | rl2[0]
        
                # Now we have the rectangle ---------------------------------------------------
                ###### 
                # select the words which at least intersect the rect
                #------------------------------------------------------------------------------
                mywords = [w for w in self.words[pno] if fitz.Rect(w[:4]).intersects(rect)]
                # print(mywords[0])
                # Sort by y1 (create lines):
                mywords.sort(key = itemgetter(3, 0))
                group = groupby(mywords, key = itemgetter(3))
                lines = []
                begin_data = None
                end_data = None
                end_of_data = "Resumo dos Negócios"
                for i, (y1, gwords) in enumerate(group):
                    line = " ".join(w[4] for w in gwords)
                    # print(line)    
                    lines.append(line)
                    if line[0:len(headers[0])] == headers[0]:
                        begin_data = i + 1
                    if line[0:len(end_of_data)] == end_of_data:
                        end_data = i
                transactions = self.group(lines[begin_data:end_data], 2)
            
                for transaction in transactions:
                    if transaction and transaction[0][0].isnumeric():
                        negotiations.append(transaction)
                self.negotiations.append(negotiations)
            self.transactions.append(transactions) # What about more than one group of transaction per file???
        return self.transactions
                    
    def get_transactions_for_options(self):
        print("Getting Options Transactions")
        transactions = None
        negotiations = []
        headers = ["Q Negociação", "C/V", "Tipo de Mercado","Prazo", "Especificação do Título", "Obs", "Quantidade", "Preço/Ajuste", "Valor/Ajuste", "D/C"]
        # 5-SOMA C VIS 2 1.855,00 3.710,00 D
        for pno, page in enumerate(self.pages):

            ##### FIRST TYPE: Regular BOVESPA Transaction (Stocks and REITs)
            ### Get transactions for ações e fii:
            rl1 = page.searchFor("Depósito / Opções") 
            rl2 = page.searchFor("Resumo dos Negócios")       # rect list two
            # print(rl1)
            # print(rl2)
            if rl1 and rl2:
                # From the two search itens, we start from far left to far right.
                rl1 = [fitz.Rect(0,rl1[0].y0,601,rl1[0].y1)]
                rl2 = [fitz.Rect(0,rl2[0].y0,601,rl2[0].y1)]
                
                rect = rl1[0] | rl2[0]
        
                # Now we have the rectangle ---------------------------------------------------
                ###### 
                # select the words which at least intersect the rect
                #------------------------------------------------------------------------------
                mywords = [w for w in self.words[pno] if fitz.Rect(w[:4]).intersects(rect)]
                # print(mywords[0])
                # Sort by y1 (create lines):
                mywords.sort(key = itemgetter(3, 0))
                group = groupby(mywords, key = itemgetter(3))
                lines = []
                begin_data = None
                end_data = None
                end_of_data = "Resumo dos Negócios"
                for i, (y1, gwords) in enumerate(group):
                    line = " ".join(w[4] for w in gwords)
                    # print(line)    
                    lines.append(line)
                    if line[0:len(headers[0])] == headers[0]:
                        begin_data = i + 1
                    if line[0:len(end_of_data)] == end_of_data:
                        end_data = i
                transactions = self.group(lines[begin_data:end_data], 2)
            
                for transaction in transactions:
                    if transaction and transaction[0][0].isnumeric():
                        negotiations.append(transaction)
            self.negotiations.append(negotiations)
            self.transactions.append(transactions) # What about more than one group of transaction per file???
        return self.transactions

    def get_financial_resume(self):
        """
        -------------------------------------------------------------------------------
        Identify the rectangle. We use the text search function here. The two
        search strings are chosen to be unique, to make our case work.
        The two returned rectangle lists both have only one item.
        -------------------------------------------------------------------------------
        """
        my_financial_resume = {}
        for pno, page in enumerate(self.pages):
            rl1 = page.searchFor("Resumo Financeiro") 
            if not rl1:
                rl1 = page.searchFor("Corretagem / Despesas") # Are we on the other page??
                if not rl1:
                    continue # I don´t need you anymore...
            rl2 = page.searchFor("Líquido para ")       # rect list two
            if rl2:
                rl2 = [rl2[0] | [(601,842),(0,0)][0]]
            else:
                rl2 = [(601,842),(0,0)]

            rect = rl1[0] | rl2[0]
    
            # Now we have the rectangle ---------------------------------------------------
            ###### 
            # select the words which at least intersect the rect
            #------------------------------------------------------------------------------
            mywords = [w for w in self.words[pno] if fitz.Rect(w[:4]).intersects(rect)]
            mywords.sort(key = itemgetter(3, 0))
            group = groupby(mywords, key = itemgetter(3))
            old = ""
            for y1, gwords in group:
                
                line = " ".join(w[4] for w in gwords)
                headers = ["Valor líquido das operações", "Taxa de liquidação", "Taxa de Registro", 
                "Total CBLC", "Taxa de termo/opções", "Taxa A.N.A", "Emolumentos",
                 "Total Bovespa / Soma", "Corretagem", "ISS", 
                 "I.R.R.F.", "Outras Bovespa", "Total Corretagem / Despesas", "Líquido para"]
                for header in headers:
                    # Did we find the header in the text content?
                    if line[0:len(header)] == header:
                        # Do you already exists?
                        if header in my_financial_resume.keys():
                            # it will append old since it appears before the label (header)
                            my_financial_resume[header].append(old)
                        else:
                            # Create the value in a list.
                            my_financial_resume[header] = [old] 
                # Regex, do your magic and show me the Money!!  XX.XXX,XX Y (Y = C or D)
                old = re.findall(r"(?:[1-9]\d{0,2}(?:\.\d{3})*|0)(?:,\d{1,2})[ ][CD]{1}", line)
                if old:
                    old = old[0]
                else:
                    old = 0
                    
        
        print("Total de Notas de Corretagem no Arquivo:", self.nc_quantity)
        for nc in range(self.nc_quantity):
            try:
                # Remove 'falsy"  items...
                my_financial_resume["Corretagem"] = [x for x in my_financial_resume["Corretagem"] if x] 
                for head in headers:
                    self.ncs_in_file[nc][head] =  my_financial_resume[head][nc]
                # my_financial_resume["Custos Totais"][nc] = float(my_financial_resume[headers[-1]][nc].split(" ")[0]) - float(my_financial_resume[headers[0][nc]].split(" ")[0])
                vl = to_money(self.ncs_in_file[nc]["Valor líquido das operações"])
                vc = to_money( self.ncs_in_file[nc]["Líquido para"])
                if "Custos Totais" in my_financial_resume.keys():
                    my_financial_resume["Custos Totais"].append(locale.currency( abs(vc - vl), grouping = True )) 
                else:
                    my_financial_resume["Custos Totais"] = [locale.currency( abs(vc - vl), grouping = True )]
                print("Nota de Corretagem Nº:", self.ncs_in_file[nc]["Nota"])
                print("Código do Cliente:", self.ncs_in_file[nc]["CodigoCliente"])
                print("Data da Nota:", self.ncs_in_file[nc]["Data"])
                for head in headers:
                    tab = "\t" if head[0:5] == "Total" else ""
                
                    print("\t {} {}: {}".format(tab, head,my_financial_resume[head][nc]))
                print("\nResumo:")
                print("\t Valor Líquido das Operações:", self.ncs_in_file[nc]["Valor líquido das operações"])
                print("\t Valor da Nota de Corretagem:", self.ncs_in_file[nc]["Líquido para"])
                print("\t Custos Totais:", my_financial_resume["Custos Totais"][nc])
                print(" -------- Negociações -------- " )
                self.get_transactions()

                print(*[(w[1], w[0].split(" ")) for w in self.negotiations], sep="\n")
                print(" ______________________________")
            except:
                print("Conta: ", self.get_account())
                for nc in range(self.nc_quantity):
                    print("Nota de Corretagem Nº:", self.ncs_in_file[nc]["Nota"])
                print("Day Trade - To be implemented!")
        self.financial_resume = my_financial_resume
        return self.financial_resume

    def group(self, lst, n):
        """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
        
        Group a list into consecutive n-tuples. Incomplete tuples are
        discarded e.g.
        
        >>> group(range(10), 3)
        [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        """
        return list(zip(*[lst[i::n] for i in range(n)]))

base_path = os.path.dirname(os.path.realpath(__file__))

my_files = os.path.join(base_path,"pdf")
my_tests = os.path.join(base_path,"tests_pdfs")

options = "/Users/maion/OneDrive/Documentos/Documentos Felipe/programs/ruby/Python/PyCharmProjects/IR/Notas Corretagem/pdf/240303-20180126-NC10439371.pdf"

brokeage_options = Document(os.path.join(my_files,options))
all_brokeage_notes = []
for file in os.listdir(my_files):
    if file.endswith(".pdf"):
        brokeage_notes = Document(os.path.join(my_files,file))
        all_brokeage_notes.append(brokeage_notes)
        brokeage_id = []
        # Concatenate the brokeage´s ids, if there are more than one "Nota de Corretagem" per file.
        for note in brokeage_notes.ncs_in_file:
            brokeage_id.append(note["Nota"])
        file_name = str(brokeage_notes.account) + "-" + str(brokeage_notes.formatedDate) + "-NC" + "-".join(brokeage_id)
    if file != file_name + '.pdf':
        print('renaming "'+ os.path.join(my_files,file) + '" to "' + file_name + '.pdf"')
        # os.system('rename "'+ os.path.join(my_files,file) + '" "' + file_name + '.pdf"')
        os.system('mv "'+ os.path.join(my_files,file) + '" "' + os.path.join(my_files,file_name) + '.pdf"')
    print("-------")


def get_biggest(all_brokeage_notes=all_brokeage_notes):
    # Returns the Index of the Brokeage Notes that has more transactions
    biggest = []
    for i, brokeage in enumerate(all_brokeage_notes):
        if brokeage.transactions:
            biggest.append((len(brokeage.transactions), i))
    return all_brokeage_notes[max(biggest, key=lambda x:x[0])[1]]



big = get_biggest()

big_financial_resume = big.financial_resume

# vl = to_money(my_financial_resume["Valor líquido das operações"][0])

# vc = to_money(my_financial_resume["Líquido para"][0])

# custos_totais = vc - vl 


# Meus gastos com corretagem até hoje (sem day trade!):
sum_costs =0 
sum_net_for = 0
sum_neg = 0
for brokeage in all_brokeage_notes: 
    if brokeage.financial_resume: 
        sum_costs += locale.atof(re.findall(r"(?:[1-9]\d{0,2}(?:\.\d{3})*|0)(?:,\d{1,2})",brokeage.financial_resume["Custos Totais"][0])[0])
        sum_net_for += to_money(brokeage.financial_resume["Líquido para"][0]) 
        # print(brokeage.date)
        for negotiations in brokeage.negotiations:
            for negotiation in negotiations:
                if negotiation:
                    sum_neg += to_money(re.findall(r"(?:[1-9]\d{0,2}(?:\.\d{3})*|0)(?:,\d{1,2})[ ][CD]{1}",negotiation[0])[0])
sum_costs = locale.currency( sum_costs, grouping = True )
sum_net_for = locale.currency( sum_net_for, grouping = True )
sum_neg = locale.currency( sum_neg, grouping = True )

print("Total Costs:", sum_costs)
print("Total Net (for):", sum_net_for)
print("Total Negotiations:", sum_neg)