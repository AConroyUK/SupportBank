import sys
import re
import logging
import transactionHandler
import fileHandler

files = ['Transactions2014.csv','DodgyTransactions2015.csv','Transactions2012.xml','Transactions2013.json']

logging.basicConfig(filename='SupportBank.log',filemode='w',
level=logging.DEBUG)

tHandler = transactionHandler.transactionHandler()
fHandler = fileHandler.fileHandler(tHandler)

def main(argv):
    for file in files:
        fHandler.importfile(file)
    response = ""
    print()
    while response != "Quit":
        print("Enter a command(List All/List[accountname]/Import filename/Quit):")
        response = input()
        if response == "List All":
            tHandler.listAll()
        elif re.fullmatch("List\[[A-Z][a-z]+ ?[A-Z]?\]",response) != None:
            account = response.split("[")[len(response.split("["))-1]
            account = account[:-1]
            tHandler.listAccount(account)
        elif response.split()[0] == "Import":
            fHandler.importfile(response.split()[1])
        elif response != "Quit":
            print("invalid user response")
            logging.info("invalid user response:" + "\"" + str(response)+ "\"")

if __name__ == "__main__":
    main(sys.argv[1:])
