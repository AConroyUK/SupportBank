import re
import logging
from datetime import datetime
from datetime import timedelta

class transaction:
    def __init__(self,date,fromAccount,toAccount,narrative,amount):
        self.date = date
        self.fromAccount = fromAccount
        self.toAccount = toAccount
        self.narrative = narrative
        self.amount = amount

class transactionHandler:
    def __init__(self):
        self.transactions = []
        self.accounts = {}
        self.maxlengths = [0,0,0,0,0]

    def listAll(self):
        string = "| " + "Account".ljust(self.maxlengths[1]) + " | " + \
            "Balance".ljust(10) + "|"
        print(string)
        print("-"*len(string))
        for i in self.accounts:
            string = i.ljust(self.maxlengths[1]) + " | "
            balance = str(self.accounts[i])
            balance = balance[:balance.find(".")+3]
            index = len(balance) - balance.find(".")
            if index < 3:
                balance = balance.ljust(len(balance)+(3-index),'0')
            print("| " + string + balance.rjust(10) + "|")

    def listAccount(self,accountname):
        if accountname in self.accounts:
            string = "| " + "Date".ljust(self.maxlengths[0]) + " | " + "From".ljust(self.maxlengths[1]) + \
                " | " + "To".ljust(self.maxlengths[2]) + " | " + "Description".ljust(self.maxlengths[3]) + \
                " | " + "Amount".ljust(self.maxlengths[4]) + "|"
            print(string)
            print("-"*len(string))
            for i in self.transactions:
                if accountname==i.fromAccount or accountname==i.toAccount:
                    string = "| "
                    string = string + i.date.strftime("%d/%m/%Y").ljust(self.maxlengths[0]) + " | "
                    string = string + i.fromAccount.ljust(self.maxlengths[1]) + " | "
                    string = string + i.toAccount.ljust(self.maxlengths[2]) + " | "
                    string = string + i.narrative.ljust(self.maxlengths[3]) + " | "
                    balance = i.amount
                    index = len(balance) - balance.find(".")
                    if index < 3:
                        balance = balance.ljust(len(balance)+(3-index),'0')
                    string = string + balance.rjust(self.maxlengths[4]) + " | "
                    print(string)
        else:
            print("Account not found")
            logging.info("Account not found:" + "\"" + str(accountname)+ "\"")

    def readRow(self,row):
        #takes a list, example:['01/03/2015', 'Ben B', 'Sam N', 'Lunch', '3.80']
        if re.fullmatch("(^[0-9]{2,4}[/-][0-9]{2}[/-][0-9]{2,4}$)|[0-9]+",row[0]) != None and \
        re.fullmatch("^[0-9]+\.?[0-9]*$",row[4]) != None:
            if re.fullmatch("(^[0-9]{2}/[0-9]{2}/[0-9]{4}$)",row[0]) != None:
                date = datetime.strptime(row[0],"%d/%m/%Y")
            elif re.fullmatch("(^[0-9]{4}-[0-9]{2}-[0-9]{2}$)",row[0]) != None:
                date = datetime.strptime(row[0],"%Y-%m-%d")
            elif re.fullmatch("(^[0-9]+$)",row[0]) != None:
                #python epoch = 01/01/1970 xml file date based on excel epoch = 01/01/1900
                date = datetime(1899,12,30) + timedelta(int(row[0]))

            self.transactions.append(transaction(date,row[1],row[2],row[3],row[4]))

            for i in range(len(row)):
                if len(row[i]) > self.maxlengths[i]:
                    self.maxlengths[i] = len(row[i])
            if row[1] in self.accounts:
                self.accounts[row[1]] -= float(row[4])
            else: self.accounts[row[1]] = 0 - float(row[4])
            if row[2] in self.accounts:
                self.accounts[row[2]] += float(row[4])
            else: self.accounts[row[2]] = float(row[4])
        else:
            logging.info("Row ignored, invalid data:" + str(row))
