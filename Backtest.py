## Author: Britton K. Deets
## Created: July 14th , 2018

import CollectData
import Trade
import matplotlib.pyplot as plt
import pprint


class Backtest:

    #Needed for class initialization
    balance = 0
    balances = []
    granularity = "D" #default
    strategy = "undef"
    strat_args = "undef"

    #Initialized after startBacktest
    results = []
    relevantData = []
    relDataChunk = []
    studies = []
    trades = []
    currTrade = None

    #Constant Variables
    SPREAD = .0002 # Need to make a dynamic value --- I think you can get spread data from the API
    EXIT_LONG = "exitLong"
    EXIT_SHORT = "exitShort"



    def __init__(self, balance, granularity, strategy, currency, strat_args):
        self.balance = balance
        self.granularity = granularity
        self.strategy = strategy
        self.strat_args = strat_args
        self.relevantData = CollectData.getData(strategy.tradespecs['supportINTD'], granularity, currency)['candles']


    def enterLong(self,index):
        self.currTrade.entryProcedures(index, float(self.relevantData[index]['mid']['c']) + Backtest.SPREAD, True)


    def enterShort(self,index):
        self.currTrade.entryProcedures(index, float(self.relevantData[index]['mid']['c']) - Backtest.SPREAD, False)


    def exitLong(self,index):
        self.currTrade.exitProcedures(index, float(self.relevantData[index]['mid']['c']) - Backtest.SPREAD)


    def exitShort(self,index):
        self.currTrade.exitProcedures(index, float(self.relevantData[index]['mid']['c']) + Backtest.SPREAD)


    indictation_dict = {
        "enterLong": enterLong,
        "enterShort": enterShort,
        "exitLong": exitLong,
        "exitShort": exitShort
    }

    def setDataChunk(self, index, period):
        if index >= period:
            self.relDataChunk = self.relevantData[index - period: index]
        elif index == 0:
            self.relDataChunk = [self.relevantData[0]]
        else:
            self.relDataChunk = self.relevantData[0:index]


    def hitStopLevel(self,index):
        pct_change = (float(self.relevantData[index]['mid']['c']) - self.currTrade.getEntryPrice())/self.currTrade.getEntryPrice()
        if strat_args['profitDistance']:
            if pct_change > strat_args['profitDistance']:
                return True
        elif strat_args['stopDistance']:
            if abs(pct_change) > strat_args['stopDistance']:
                return True
        return False


    def changeBalance(self, indication):
        if indication == "exitLong":
            self.balance = (1 + self.currTrade.getPctChange()) * self.balance
        else:
            self.balance = (1 - self.currTrade.getPctChange()) * self.balance


    def trade(self,indication, index):
        action = Backtest.indictation_dict[indication]

        if indication.startswith("exit"):
            action(self,index)
            self.changeBalance(indication)
            self.trades.append(self.currTrade)
            self.balances.append(self.balance)

        elif indication.startswith("enter"):
            action(self, index)


    def startBacktest(self):
        for index, datapoint in enumerate(self.relevantData):
            self.setDataChunk(index,self.strat_args['period'])
            if self.currTrade:
                indication, study = self.strategy.main(self.relDataChunk, self.currTrade.getIsOpen(), self.currTrade.getIsLong(), self.strat_args)
            else:
                indication, study = self.strategy.main(self.relDataChunk, False, None, self.strat_args)

            if indication:
                if indication.startswith("enter"):
                    self.studies.append(study)
                    self.currTrade = Trade.Trade(index)
                    self.trade(indication, index)
                else:
                    self.studies.append(study)
                    self.trade(indication, index)

            elif self.currTrade:
                self.studies.append(study)

                if self.currTrade.getIsOpen() and self.hitStopLevel(index):
                    if self.currTrade.getIsLong():
                        self.trade(self.EXIT_LONG,index)
                    else:
                        self.trade(self.EXIT_SHORT, index)

            else:
                self.studies.append(study)




balance = 1000
strat_args = {
    'period': 50,
    'distance': .05,
    'stopDistance': False,
    'profitDistance': False
}
currency = "GBP_USD"
granularity = "D"

from Strategies.MA import strategy

backtest = Backtest(balance, granularity, strategy, currency, strat_args)
backtest.startBacktest()

balance = backtest.balances[-1]
tradeData = backtest.trades
print(balance)

# index_price = [(tdata[-1], tdata[0]) for tdata in tradeData]
close_prices = [float(candle['mid']['c']) for candle in backtest.relevantData]
plt.plot(close_prices)
plt.plot(backtest.studies)

for tradeObj in tradeData:
    output = tradeObj.toList()
    if tradeObj.getIsLong():
        plt.plot(tradeObj.getStartIndex(), tradeObj.getEntryPrice(), "g+")
        plt.plot(tradeObj.getEndIndex(), tradeObj.getExitPrice(), "rx")
    else:
        plt.plot(tradeObj.getStartIndex(), tradeObj.getEntryPrice(), "b+")
        plt.plot(tradeObj.getEndIndex(), tradeObj.getExitPrice(), "rx")

for td in tradeData:
    print(td.toList())

plt.show()

plt.plot(backtest.balances)
plt.show()
### In a display file ###

## Want to see plot of the trades
## Want to see plot of the balances
## Want to see trade data
## Descriptive statistics
## STANDARD DEVIATION IS KEY

### Should I do this with a front-end application????????????????? ###
## Generate an html page perhaps ##
