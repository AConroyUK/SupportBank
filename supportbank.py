import csv
import sys
from pprint import pprint

def main(argv):
    transactions = []
    accounts = {}
    maxlengths = [0,0,0,0,0]
    with open('Transactions2014.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        index = 0
        for row in csvreader:
            if index > 0:
                transactions.append(row)
                for i in range(len(row)):
                    if len(row[i]) > maxlengths[i]:
                        maxlengths[i] = len(row[i])
                if row[1] in accounts:
                    accounts[row[1]] -= float(row[4])
                else: accounts[row[1]] = 0 - float(row[4])
                if row[2] in accounts:
                    accounts[row[2]] += float(row[4])
                else: accounts[row[2]] = float(row[4])

            index += 1

    response = ""
    while response != "Quit":
        print("Enter a command('List All'/'List[accountname]'/'Quit'):")
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
                print("| " + string + balance.rjust(10) + "|")
        else:
            account = response.split("[")[len(response.split("["))-1]
            account = account[:-1]
            if account in accounts:
                string = "| " + "Date".ljust(maxlengths[0]) + " | " + "From".ljust(maxlengths[1]) + \
                    " | " + "To".ljust(maxlengths[2]) + " | " + "Narritave".ljust(maxlengths[3]) + \
                    " | " + "Amount".ljust(maxlengths[4]) + "|"
                print(string)
                print("-"*len(string))
                for i in transactions:
                    if account==i[1] or account==i[2]:
                        string = "| "
                        for j in range(len(i)):
                            string = string + i[j].ljust(maxlengths[j]) + " | "
                        print(string)

if __name__ == "__main__":
    main(sys.argv[1:])
