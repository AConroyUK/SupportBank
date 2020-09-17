import csv
import logging
import json
import xml.etree.ElementTree as ET

class fileHandler:
    def __init__(self,tHandler):
        self.tHandler = tHandler

    def loadconfig(self):
        with open('supportbank.config') as configfile:
            configs = []
            for line in configfile:
                configs.append(line[:-1])
            DEBUG_LEVEL = configs[0].split("=")[1]
            EXPORT_FILENAME = configs[1].split("=")[1]
            EXPORT_FORMAT = configs[2].split("=")[1]
        return DEBUG_LEVEL, EXPORT_FILENAME, EXPORT_FORMAT

    def exportAccount(self,account,filename,format):
        transaction_data = self.tHandler.listAccount(account,format)
        if transaction_data != []:
            filename += "." + format
            if format == "txt":
                with open(filename, 'w') as exportfile:
                    for transaction in transaction_data:
                        exportfile.write(transaction + "\n")
                logging.info("Exported account[" + account + "]")
            elif format == "csv":
                with open(filename, 'w') as exportfile:
                    for transaction in transaction_data:
                        exportfile.write(transaction[0]+","+transaction[1]+\
                        ","+transaction[2]+","+transaction[3]+","+transaction[4]+"\n")
                logging.info("Exported account[" + account + "]")
            elif format == "json":
                with open(filename, 'w') as exportfile:
                    exportfile.write("[\n")
                    for transaction in transaction_data[1:]:
                        dict = {
                            "date": str(transaction[0]),
                            "fromAccount": str(transaction[1]),
                            "toAccount": str(transaction[2]),
                            "narrative": str(transaction[3]),
                            "amount": transaction[4]
                        }
                        exportfile.write(json.dumps(dict, indent=2)+",\n")
                    exportfile.write("]")
                logging.info("Exported account[" + account + "]")
            else:
                logging.info("Unrecognised file format, unable to export to " + filename)

    def importfile(self,path):
        type = path[path.find(".")+1:]
        if type == "json":
            self.importjson(path)
        elif type == "csv":
            self.importcsv(path)
        elif type == "xml":
            self.importxml(path)

    def importjson(self,path):
        with open(path) as jsonfile:
            data = json.load(jsonfile)
            for dict in data:
                date = str(dict["date"])
                fromAccount = str(dict["fromAccount"])
                toAccount = str(dict["toAccount"])
                narrative = str(dict["narrative"])
                amount = str(dict["amount"])
                self.tHandler.readRow([date,fromAccount,toAccount,narrative,amount])
        logging.info("Imported file:" + str(path))
        self.tHandler.transactions.sort(key=self.sortKey)

    def importcsv(self,path):
        with open(path, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            index = 0
            for row in csvreader:
                if index > 0:
                    self.tHandler.readRow(row)
                index += 1
        logging.info("Imported file:" + str(path))
        self.tHandler.transactions.sort(key=self.sortKey)

    def importxml(self,path):
        tree = ET.parse(path)
        root = tree.getroot()
        for transaction in root.findall('SupportTransaction'):
            date = transaction.get('Date')
            description = transaction.find('Description').text
            value = transaction.find('Value').text
            parties = transaction.find('Parties')
            fromAccount = parties.find('From').text
            toAccount = parties.find('To').text
            self.tHandler.readRow([date, fromAccount, toAccount ,description, value])
        logging.info("Imported file:" + str(path))
        self.tHandler.transactions.sort(key=self.sortKey)

    def sortKey(self,transaction):
        return transaction.date
