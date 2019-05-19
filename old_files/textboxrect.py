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

# Definir Orquestrador:
# Abrir PDF
# Processar páginas
# Ver quantidades de Notas de Corretagem por arquivo


class NotaCorretagem:
    def __init__(self, data = None, nota=None, valor_liq=None, valor_nc=None, conta = None):
        self.data = data
        self.nota = nota
        self.valor_liq = valor_liq
        self.valor_nc = valor_nc
        self.conta = conta

base_path = os.path.dirname(os.path.realpath(__file__))

my_files = os.path.join(base_path,"pdf")

# some_file = os.path.join(my_files, "59448-20140711-NC5311691.pdf")
# some_file = os.path.join(my_files, "59448-20140717-NC5325064.pdf")
# some_file = os.path.join(my_files, "59448-20121207-NC3819768.pdf")

def extrair_nc(some_file):
    print("Processando:", some_file)
    qnt_de_nc = 0
    
    notas_no_aquivo = []

    resumo = []
    doc = fitz.open(some_file)     # any supported document type
    num_of_pages = doc.pageCount
    for pno in range(0,num_of_pages):
        rl1, rl2 = None, None
        # print("Processando página:", pno)
        page = doc[pno]                    # we want text from this page

        """
        Get all words on page in a list of lists. Each word is represented by:
        [x0, y0, x1, y1, word, bno, lno, wno]
        The first 4 entries are the word's rectangle coordinates, the last 3 are just
        technical info (block number, line number, word number).
        """
        words = page.getTextWords()
        # We subselect from above list.
        # if pno == 0:

        rl1 = page.searchFor("Data pregão:")
        rl2 = page.searchFor("C.I")
        # print(rl1)
        if rl1:
            ## Opening new NotaCorretagem
            nota_de_corretagem = {}
            pregao = []
            txt = ""
            resumo.append("")
            rect = rl1[0] | rl2[0]
            mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
            mywords.sort(key = itemgetter(3, 0))
            group = groupby(mywords, key = itemgetter(3))
            for y1, gwords in group:
                line = [w[4] for w in gwords]
                pregao.append(line)
                txt += " ".join(line)
            notas_no_aquivo.append(nota_de_corretagem)
            # print(txt)
            num_nota = [item for sublist in pregao for item in sublist if item.isnumeric()][0]
            
            notas_no_aquivo[qnt_de_nc]["Data"] = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", txt)[0]
            notas_no_aquivo[qnt_de_nc]["Nota"] = num_nota #re.findall(r"[0-9]{5,}", txt)[0]
            split_data = notas_no_aquivo[qnt_de_nc]["Data"].split("/")
            notas_no_aquivo[qnt_de_nc]["FormatoData"] = split_data[-1]+split_data[-2]+ split_data[-3]
            # print(txt)
            # input()
            resumo[qnt_de_nc] += "--------------------- "
            qnt_de_nc += 1
            # print(nota_de_corretagem)
            # input()


        rl1 = page.searchFor("Conta XP")
        rl2 = [(601,842),(0,0)]
        rect = rl1[0] | rl2[0]
        codigo = []
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
        mywords.sort(key = itemgetter(3, 0))
        group = groupby(mywords, key = itemgetter(3))
        for y1, gwords in group:
            info = " ".join(w[4] for w in gwords)
            codigo.append(info)
        notas_no_aquivo[qnt_de_nc - 1]["CodigoCliente"] = codigo[0]
            

        """
        -------------------------------------------------------------------------------
        Identify the rectangle. We use the text search function here. The two
        search strings are chosen to be unique, to make our case work.
        The two returned rectangle lists both have only one item.
        -------------------------------------------------------------------------------
        """
        rl1 = page.searchFor("Resumo Financeiro") 
        if not rl1:
            rl1 = page.searchFor("Líquido para ") # Are we on the other page??
            if not rl1:
                continue # I don´t need you anymore...
        # print(rl1)
        # try:
            # valor_liq = "48.631,56"
            # valor_liq = "584,20"
        rl2 = page.searchFor("Líquido para ")       # rect list two
        if rl2:
            rl2 = [rl2[0] | [(601,842),(0,0)][0]]
        else:
            rl2 = [(601,842),(0,0)]

        rect = rl1[0] | rl2[0]
 
        # rect = rl1[0] | rl2[0]       # union rectangle
        # Now we have the rectangle ---------------------------------------------------

        ###### https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/textboxtract.py

        # select the words which at least intersect the rect
        #------------------------------------------------------------------------------
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
        mywords.sort(key = itemgetter(3, 0))
        group = groupby(mywords, key = itemgetter(3))
        # print("\nSelect the words intersecting the rectangle")
        # print("-------------------------------------------")
        
        # resumo_list = []
        for y1, gwords in group:
            
            line = " ".join(w[4] for w in gwords)
            # resumo_list.append(line)
            resumo[qnt_de_nc - 1] += line + "\n"
        # print(resumo)
        # input()
    ### CRIAR FUNÇÂO!
    print("Total de Notas de Corretagem no Arquivo:", qnt_de_nc)
    for nc in range(qnt_de_nc):
        resumos = resumo[nc].split("--------------------- ")
        for resumo_nc in resumos:
            money = re.findall(r"(?:[1-9]\d{0,2}(?:\.\d{3})*|0)(?:,\d{1,2})[ ][CD]{1}", resumo_nc)
            # deb_cred = re.findall(r"[DC]{1}", resumo_nc)
            if money:
                valor_liq = money[0]
                valor_nc = money[-1]
                notas_no_aquivo[nc]["ValorOperacoes"] =  valor_liq
                notas_no_aquivo[nc]["ValorNota"] = valor_nc#, deb_cred[-3]
                print("Nota de Corretagem Nº:", notas_no_aquivo[nc]["Nota"])
                # Pegar código do cliente!
                print("Código do Cliente:", notas_no_aquivo[nc]["CodigoCliente"])
                print("Data da Nota:", notas_no_aquivo[nc]["Data"])
                print("Valor Líquido das Operações:", notas_no_aquivo[nc]["ValorOperacoes"])
                print("Valor da Nota de Corretagem", notas_no_aquivo[nc]["ValorNota"])
                print(" " )
    return notas_no_aquivo
        # print(resumo)


# some_file = os.path.join(my_files, "59448-20140711-NC5311691.pdf")
# nc1 = extrair_nc(some_file)
# some_file = os.path.join(my_files, "59448-20140717-NC5325064.pdf")
# nc2 = extrair_nc(some_file)
# some_file = os.path.join(my_files, "59448-20121207-NC3819768.pdf")
# nc3 = extrair_nc(some_file)

info = []
for file in os.listdir(my_files):
    if file.endswith("pdf"):
        info = extrair_nc(os.path.join(my_files,file))
        nc = ""
        if len(info) == 1:
            file_name = info[0]["CodigoCliente"] + "-" + info[0]["FormatoData"] + "-NC"+ info[0]["Nota"]
        else:
            for notas in info:
                nc += "-" + notas["Nota"]
            file_name = info[0]["CodigoCliente"] + "-" + info[0]["FormatoData"] + "-NC"+ nc
        # print(file_name)
        ### For other systems (not Windows) use mv instead of rename
        if file != file_name + '.pdf':
            print('renaming "'+ os.path.join(my_files,file) + '" to "' + file_name + '.pdf"')
            # os.system('rename "'+ os.path.join(my_files,file) + '" "' + file_name + '.pdf"')
            os.system('mv "'+ os.path.join(my_files,file) + '" "' + os.path.join(my_files,file_name) + '.pdf"')

        print("---------")
        # print("---------")