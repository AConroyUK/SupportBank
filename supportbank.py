import csv
import sys
import re
import logging
import json
import xml.etree.ElementTree as ET
import transactionHandler

files = ['Transactions2014.csv','DodgyTransactions2015.csv','Transactions2012.xml','Transactions2013.json']

logging.basicConfig(filename='SupportBank.log',filemode='w',
level=logging.DEBUG)

tHandler = transactionHandler.transactionHandler()

def importfile(path):
    type = path[path.find(".")+1:]
    if type == "json":
        importjson(path)
    elif type == "csv":
        importcsv(path)
    elif type == "xml":
        importxml(path)

def importjson(path):
    with open(path) as jsonfile:
        data = json.load(jsonfile)
        for dict in data:
            date = str(dict["date"])
            fromAccount = str(dict["fromAccount"])
            toAccount = str(dict["toAccount"])
            narrative = str(dict["narrative"])
            amount = str(dict["amount"])
            tHandler.readRow([date,fromAccount,toAccount,narrative,amount])
    logging.info("Imported file:" + str(path))
    tHandler.transactions.sort(key=sortKey)

def importcsv(path):
    with open(path, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        index = 0
        for row in csvreader:
            if index > 0:
                tHandler.readRow(row)
            index += 1
    logging.info("Imported file:" + str(path))
    tHandler.transactions.sort(key=sortKey)

def importxml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for transaction in root.findall('SupportTransaction'):
        date = transaction.get('Date')
        description = transaction.find('Description').text
        value = transaction.find('Value').text
        parties = transaction.find('Parties')
        fromAccount = parties.find('From').text
        toAccount = parties.find('To').text
        tHandler.readRow([date, fromAccount, toAccount ,description, value])
    logging.info("Imported file:" + str(path))
    tHandler.transactions.sort(key=sortKey)

def sortKey(transaction):
    return transaction.date

def main(argv):
    for file in files:
        importfile(file)
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
            importfile(response.split()[1])
        elif response != "Quit":
            print("invalid user response")
            logging.info("invalid user response:" + "\"" + str(response)+ "\"")

if __name__ == "__main__":
    main(sys.argv[1:])
