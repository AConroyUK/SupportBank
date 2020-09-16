import csv
import logging
import json
import xml.etree.ElementTree as ET

class fileHandler:
    def __init__(self,tHandler):
        self.tHandler = tHandler

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
