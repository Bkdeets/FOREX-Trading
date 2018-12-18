import json
import requests


class ProductionAPI:
    acctDetails = {}

    def __init__(self):
        with open("acctdetails") as file:
            self.acctDetails = json.load(file)

    #################### Account Endpoints ##########################
    def getAccountSummary(self):
        URL = self.acctDetails['baseURL'] + "/accounts/" + self.acctDetails['accountID']
        headers = self.acctDetails['headers']
        acctSummary = json.loads(json.dumps(requests.get(URL, headers=headers).json()))
        return acctSummary

    def getAccountBalance(self):
        return float(self.getAccountSummary()['account']['balance'])

    def getMarginAvailable(self):
        return float(self.getAccountSummary()['account']['marginAvailable'])


    #################### Instrument endpoints #######################
    def getPriceData(self, currencyPair, numberOfCandles, granularity):
        URL = self.acctDetails['baseURL'] + "/instruments/" + currencyPair + "/candles"
        query = {
            "granularity": granularity,
            "count": numberOfCandles
        }
        headers = self.acctDetails['headers']
        return json.loads(json.dumps(requests.get(URL,headers=headers, query=query).json()))

    def getCurrentPrice(self, currencyPair):
        currentData = self.getPriceData(currencyPair, 2, "M1")
        return float(currentData['candles'][-1]['mid']['c'])

    #################### Trade Entry/Exit Endpoints ############################
    def enterLong(self, currencyPair, stopLoss, takeProfit, tradeAmount):
        return None

    def enterShort(self, currencyPair, stopLoss, takeProfit, tradeAmount):
        return None

    def exitLong(self, tradeId):
        return None

    def exitShort(self, tradeId):
        return None


    #################### Trade Management Endpoints ##########################
    def setStopLoss(self, tradeId, stopLevel):
        return None

    def setTakeProfit(self, tradeId, profitLevel):
        return None

    def getTradePL(self, tradeId):
        return None

    def getTradeInformation(self, tradeId):
        return None

