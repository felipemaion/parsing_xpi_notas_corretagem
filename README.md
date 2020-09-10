# PARSING XPI's pdf 'NOTAS DE CORRETAGEM'
Parsing and classifying information downloaded from XP Investimentos (Notas de Corretagem)  (Brokerage Notes)


# HOW TO USE

-  To download the notas de corretagens:
    Login into your account, go to the page of the Brokeage Notes. Select the oldest file. 
    Download it, as you normally would (I recommend using XP format)
    Run the script 
    ```python nc_auto.py```

    It should download the rest of the files... NOTE: You cannot use your computer, nor move your mouse during the process... since it works identifying the controls of the page, and moving and clicking to do it.

After that:
- To Parse the information:

put the files into the folder 'pdf' and run the script:

```ipython -i parse_pdfs.py```

It will parse the information from the pdfs to txt files, and classify.

Currently only classifying stocks, REITs and Options.


# ToDO
Wow... there are a lot to do here..
- Identify the Daytrades.
- Create the JSON
- Refactor the code.
- organize the information better.