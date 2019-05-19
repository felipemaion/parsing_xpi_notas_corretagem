import os
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

dir_path = os.path.dirname(os.path.realpath(__file__))
# for file in os.listdir(dir_path):
#     if file.endswith(".pdf"):
#         # print(os.path.join(dir_path, file))
#         # print("Converting file:", str(file))
#         cmd = "pdftotext '" + os.path.join(dir_path, file) + "'"
#         print(cmd)
#         os.system(cmd)

path = os.path.join(dir_path, "240303.pdf")
fp = open(path, 'rb')


parser = PDFParser(fp)
doc = PDFDocument()
parser.set_document(doc)
doc.set_parser(parser)
doc.initialize('')
rsrcmgr = PDFResourceManager()
laparams = LAParams()
laparams.char_margin = 1.0
laparams.word_margin = 1.0
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
extracted_text = ''

for page in doc.get_pages():
    interpreter.process_page(page)
    layout = device.get_result()
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            extracted_text += lt_obj.get_text()

with open('convertedFile.txt',"wb") as txt_file:
    txt_file.write(extracted_text.encode("utf-8"))