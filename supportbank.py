import csv
import sys
import re
import logging
import json
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET


csvfiles = ['Transactions2014.csv','DodgyTransactions2015.csv']
transactions = []
accounts = {}
maxlengths = [0,0,0,0,0]

logging.basicConfig(filename='SupportBank.log',filemode='w',
level=logging.DEBUG)

class transaction:
    def __init__(self,date,fromAccount,toAccount,narrative,amount):
        self.date = date
        self.fromAccount = fromAccount
        self.toAccount = toAccount
        self.narrative = narrative
        self.amount = amount


def readRow(row):
    #takes a list, example:['01/03/2015', 'Ben B', 'Sam N', 'Lunch', '3.80']
    if re.fullmatch("(^[0-9]{2,4}[/-][0-9]{2}[/-][0-9]{2,4}$)|[0-9]+",row[0]) != None and \
    re.fullmatch("^[0-9]+\.?[0-9]*$",row[4]) != None:
        #transactions.append(row)
        if re.fullmatch("(^[0-9]{2}/[0-9]{2}/[0-9]{4}$)",row[0]) != None:
            date = datetime.strptime(row[0],"%d/%m/%Y")
        elif re.fullmatch("(^[0-9]{4}-[0-9]{2}-[0-9]{2}$)",row[0]) != None:
            date = datetime.strptime(row[0],"%Y-%m-%d")
        elif re.fullmatch("(^[0-9]+$)",row[0]) != None:
            #python epoch = 01/01/1970 xml file date based on excel epoch = 01/01/1900
            date = datetime(1899,12,30) + timedelta(int(row[0]))

        transactions.append(transaction(date,row[1],row[2],row[3],row[4]))

        for i in range(len(row)):
            if len(row[i]) > maxlengths[i]:
                maxlengths[i] = len(row[i])
        if row[1] in accounts:
            accounts[row[1]] -= float(row[4])
        else: accounts[row[1]] = 0 - float(row[4])
        if row[2] in accounts:
            accounts[row[2]] += float(row[4])
        else: accounts[row[2]] = float(row[4])
    else:
        logging.info("Row ignored, invalid data:" + str(row))

def importjson(path):
    with open(path) as jsonfile:
        data = json.load(jsonfile)
        for dict in data:
            row = []
            row.append(str(dict["date"]))
            row.append(str(dict["fromAccount"]))
            row.append(str(dict["toAccount"]))
            row.append(str(dict["narrative"]))
            row.append(str(dict["amount"]))
            readRow(row)
    logging.info("Imported file:" + str(path))
    transactions.sort(key=sortKey)

def importcsv(path):
    with open(path, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        index = 0
        for row in csvreader:
            if index > 0:
                readRow(row)
            index += 1
    logging.info("Imported file:" + str(path))
    transactions.sort(key=sortKey)

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
        #print(date, fromAccount, toAccount ,description, value)
        readRow([date, fromAccount, toAccount ,description, value])

    logging.info("Imported file:" + str(path))
    transactions.sort(key=sortKey)

def sortKey(transaction):
    return transaction.date

def main(argv):
    for file in csvfiles:
        importcsv(file)
    response = ""
    print()
    while response != "Quit":
        print("Enter a command(List All/List[accountname]/Import filename/Quit):")
        response = input()
        if response == "List All":
            string = "| " + "Account".ljust(maxlengths[1]) + " | " + \
                "Balance".ljust(10) + "|"
            print(string)
            print("-"*len(string))
            for i in accounts:
                string = i.ljust(maxlengths[1]) + " | "
                balance = str(accounts[i])
                balance = balance[:balance.find(".")+3]
                index = len(balance) - balance.find(".")
                if index < 3:
                    balance = balance.ljust(len(balance)+(3-index),'0')
                print("| " + string + balance.rjust(10) + "|")
        elif re.fullmatch("List\[[A-Z][a-z]+ ?[A-Z]?\]",response) != None:
            account = response.split("[")[len(response.split("["))-1]
            account = account[:-1]
            if account in accounts:
                string = "| " + "Date".ljust(maxlengths[0]) + " | " + "From".ljust(maxlengths[1]) + \
                    " | " + "To".ljust(maxlengths[2]) + " | " + "Narritave".ljust(maxlengths[3]) + \
                    " | " + "Amount".ljust(maxlengths[4]) + "|"
                print(string)
                print("-"*len(string))
                for i in transactions:

                    if account==i.fromAccount or account==i.toAccount:
                        string = "| "
                        string = string + i.date.strftime("%d/%m/%Y").ljust(maxlengths[0]) + " | "
                        string = string + i.fromAccount.ljust(maxlengths[1]) + " | "
                        string = string + i.toAccount.ljust(maxlengths[2]) + " | "
                        string = string + i.narrative.ljust(maxlengths[3]) + " | "

                        # for j in range(len(i)-1):
                        #     string = string + i[j].ljust(maxlengths[j]) + " | "

                        balance = i.amount
                        index = len(balance) - balance.find(".")
                        if index < 3:
                            balance = balance.ljust(len(balance)+(3-index),'0')

                        string = string + balance.rjust(maxlengths[4]) + " | "
                        print(string)
            else:
                print("Account not found")
                logging.info("Account not found:" + "\"" + str(account)+ "\"")
        elif response.split()[0] == "Import":
            type = response.split()[1]
            type = type[type.find(".")+1:]
            if type == "json":
                importjson(response.split()[1])
            elif type == "csv":
                importcsv(response.split()[1])
            elif type == "xml":
                importxml(response.split()[1])
        elif response != "Quit":
            print("invalid user response")
            logging.info("invalid user response:" + "\"" + str(response)+ "\"")

if __name__ == "__main__":
    main(sys.argv[1:])
