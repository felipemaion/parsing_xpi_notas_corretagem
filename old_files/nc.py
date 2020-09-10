import os
dir_path = os.path.dirname(os.path.realpath(__file__))
for file in os.listdir(dir_path):
    if file.endswith(".pdf"):
        # print(os.path.join(dir_path, file))
        # print("Converting file:", str(file))
        cmd = "pdftotext '" + os.path.join(dir_path, file) + "'"
        print(cmd)
        os.system(cmd)