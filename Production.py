
from APIWrapper import ProductionAPI

class Production:



    #Constants
    OANDA = ProductionAPI()



    strategy = None
    strat_args = {}
    granularity = "D" #default
    allocation = 30  #percentage
    lookbackData = []
    pair = ""
    state = ""



    def __init__(self, strategy, strat_args, granularity, allocation, pair):
        self.strategy = strategy
        self.strat_args = strat_args
        self.granularity = granularity
        self.allocation = allocation
        self.pair = pair


    def beginTrading(self):

        marginAvailable = Production.OANDA.getMarginAvailable()
        tradeAmount = self.allocation * marginAvailable

        lookbackData = Production.OANDA.getPriceData(self.pair, self.strat_args.period, self.granularity)

        #consult strategy
        startingState = None
        indication, study = self.strategy.main(lookbackData, startingState, self.strat_args)

        currentPrice = Production.OANDA.getCurrentPrice(self.pair)

        #enter/exit/none depending on indication
        if indication == "enterLong":

            stopLoss = currentPrice - self.strat_args['stopLossDistance']
            takeProfit = currentPrice + self.strat_args['takeProfitDistance']
            tradeId = Production.OANDA.enterLong(self.pair,stopLoss, takeProfit, tradeAmount)

            self.state = "inLong"
            #launch open trade manager with tradeId

        elif indication == "enterShort":

            stopLoss = currentPrice + self.strat_args['stopLossDistance']
            takeProfit = currentPrice - self.strat_args['takeProfitDistance']
            tradeId = Production.OANDA.enterShort(self.pair, stopLoss, takeProfit, tradeAmount)

            self.state = "inShort"
            #launch open trade manager with tradeId

        else:
            do = "do"
            # not sure yet
            # Maybe can wait based on the granularity







