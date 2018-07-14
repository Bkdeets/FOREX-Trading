
from Backtesting import backtestTrade
import requests
import json
import accountDetails
from Training import trailingStopLevel
from Training import RSICalculation
from decimal import getcontext,Decimal

## results get weird after H6
granularities = [("M5",5),("M10",10),("M15",15)]
##granularities = [("M15",15)]
instruments = ["EUR_USD","EUR_GBP","USD_CHF","NZD_USD","GBP_USD","USD_CAD"]

def createQuery(granularity,count):
    ##granularities on http://developer.oanda.com/rest-live-v20/instrument-df/
    ## count is an int from 0 to 5000 inclusive
    query = {
        "granularity": granularity,
        "count": count
    }
    return query


# instrument = input("Input instrument: ")
# granularity = input("Input granularity: ")
# count = int(input("Input candle count: "))

def collectData(instrument,granularity,count):
    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles", headers=accountDetails.getHeaders(), params=createQuery(granularity,count))
    parsedData = json.loads(json.dumps(candleData.json()))
    candles = parsedData["candles"]
    RSIs,avgSog,avgSol = RSICalculation.calcRSI(14,candles)
    stopLevel = trailingStopLevel.main(candles)
    return candles,RSIs


##calcs sum of list###
def sumList(list):
    sum = 0
    for i in list:
        sum += i
    return sum

def trainAlgo(candles,RSIs,tp,sl,good):
    results = []

    z = 15
    for i in range(15,len(RSIs)):
        if i < z:
            continue
        if RSIs[i] >= 70:
            if good:
                resulting = backtestTrade.tradeTpSlB(candles[i],candles,RSIs,i,tp,sl)
                results.append(resulting[0])
                z = resulting[1]
            else:
                resulting = backtestTrade.tradeTpSlW(candles[i], candles, RSIs, i, tp, sl)
                results.append(resulting[0])
                z = resulting[1]

    return sumList(results)


def getBestStop(candlesx,RSIsx):
    masterResults = []
    getcontext().prec = 4
    for i in range(10,51):
        stopLevel = Decimal(i)/Decimal(10000)
        resultsB = trainAlgo(candlesx,RSIsx,stopLevel,stopLevel,True)
        resultsW = trainAlgo(candlesx,RSIsx,stopLevel,stopLevel,False)

        results = (resultsB+resultsW)/2

        masterResults.append((stopLevel,results))
    bestStopTup = max(masterResults, key=lambda x:x[1])
    return bestStopTup[0]

