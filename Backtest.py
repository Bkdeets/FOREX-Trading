## Author: Britton K. Deets
## Created: July 14th , 2018

import CollectData
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
    state = None
    results = []
    relevantData = []
    studies = []
    trades = []
    entryPrice = 0


    #Static Variables
    SPREAD = .0002 # Need to make a dynamic value --- I think you can get spread data from the API



    def __init__(self, balance, granularity, strategy, currency, strat_args):
        self.balance = balance
        self.granularity = granularity
        self.strategy = strategy
        self.strat_args = strat_args;

        specs = strategy.tradespecs
        self.relevantData = CollectData.getData(specs['supportINTD'], granularity, currency)
        self.relevantData = self.relevantData['candles']


    def enterLong(self,index):
        exePrice = float(self.relevantData[index]['mid']['c']) + Backtest.SPREAD
        self.state = "inLong"
        return [exePrice,self.state]


    def enterShort(self,index):
        exePrice = float(self.relevantData[index]['mid']['c']) - Backtest.SPREAD
        self.state = "inShort"
        return [exePrice,self.state]


    def exitLong(self,index):
        exePrice = float(self.relevantData[index]['mid']['c']) - Backtest.SPREAD
        self.state = None
        return [exePrice,self.state]


    def exitShort(self,index):
        exePrice = float(self.relevantData[index]['mid']['c']) + Backtest.SPREAD
        self.state = None
        return [exePrice,self.state]

    indictation_dict = {
        "enterLong": enterLong,
        "enterShort": enterShort,
        "exitLong": exitLong,
        "exitShort": exitShort
    }

    def getDataChunk(self, index, period):
        # Pulling the correct data to feed to the strategy
        # Pulls candle by candle until the length of the period
        if index >= period:
            relDataChunk = self.relevantData[index - period: index]
        elif index == 0:
            relDataChunk = [self.relevantData[0]]
        else:
            relDataChunk = self.relevantData[0:index]

        return relDataChunk



    def checkStopAndProfit(self, relDataChunk):

        pct_change = (float(relDataChunk[0]['mid']['c']) - self.entryPrice)/self.entryPrice
        if strat_args['profitDistance'] != False:
            if pct_change > strat_args['profitDistance']:
                return True
        elif strat_args['stopDistance'] != False:
            if abs(pct_change) > strat_args['stopDistance']:
                return True
        return False



    def trade(self,indication, index):
        action = Backtest.indictation_dict[indication]

        trade_data = []
        pct_chg = 0

        if indication.startswith("exit") and self.state != None:
            trade_data = action(self,index)
            executionPrice = trade_data[0]

            pct_chg = (executionPrice - self.entryPrice) / self.entryPrice
            if indication == "exitLong":
                self.balance = (1+pct_chg) * self.balance
            else:
                pct_chg = -pct_chg
                self.balance = (1+pct_chg) * self.balance

            trade_data.append(pct_chg)
            trade_data.append(self.balance)

        elif indication.startswith("enter"):
            trade_data = action(self, index)
            executionPrice = trade_data[0]
            self.entryPrice = executionPrice

            trade_data.append(pct_chg)
            trade_data.append(self.balance)



        # [exe_price, state, change, balance]
        return trade_data


    # Will always backtest on the largest time period given by the granularity and period specified in strategy datareq
    def startBacktest(self):

        # Initializing variables
        entryPrice = float(self.relevantData[0]['mid']['o'])
        specs = self.strategy.tradespecs
        period = self.strat_args['period']
        trade_data = []

        # Starting backtest
        for index, datapoint in enumerate(self.relevantData):

            relDataChunk = self.getDataChunk(index,period)

            # Indication can be anything in indication dict or None (False)
            # Get indication and study values from strategy
            indication, study = self.strategy.main(relDataChunk, self.state, self.strat_args)

            if indication:
                self.studies.append(study)

                #Make the trade
                trade_data = self.trade(indication, index)

                # Updating important price data
                self.entryPrice = trade_data[0]

                #Update balances list
                self.balances.append(self.balance)

                #Add the index to trade data
                trade_data.append(index)

                # Append trade data to trades list
                self.trades.append(trade_data)

            else:
                self.studies.append(study)

                if self.state != None:
                    indication = self.checkStopAndProfit(relDataChunk)
                    if indication:
                        if self.state == "inLong":
                            trade_data = self.trade("exitLong",index)
                        elif self.state == "inShort":
                            trade_data = self.trade("exitShort", index)

                        # Updating important price data
                        self.entryPrice = trade_data[0]

                        # Update balances list
                        self.balances.append(self.balance)

                        # Add the index to trade data
                        trade_data.append(index)

                        # Append trade data to trades list
                        self.trades.append(trade_data)




balance = 1000
strat_args = {
    'period': 50,
    'distance': .01,
    'stopDistance': .01,
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

for td in tradeData:
    if td[1] == "inLong":
        plt.plot(td[-1],td[0], "g+")
    elif td[1] == "inShort":
        plt.plot(td[-1], td[0], "rx")
    elif td[1] == None:
        plt.plot(td[-1], td[0], "bo")
for td in tradeData:
    print(td)

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
