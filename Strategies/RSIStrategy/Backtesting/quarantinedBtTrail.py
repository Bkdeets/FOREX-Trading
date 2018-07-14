
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




def collectData(instrument,granularity,count):
    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles", headers=accountDetails.getHeaders(), params=createQuery(granularity,count))
    parsedData = json.loads(json.dumps(candleData.json()))
    candles = parsedData["candles"]
    RSIs,avgSog,avgSol = RSICalculation.calcRSI(14,candles)
    stopLevel = trailingStopLevel.main(candles)
    return candles,RSIs


def trainAlgo(candles,RSIs,sl):
    results = []

    z = 15
    for i in range(15,len(RSIs)):
        if i < z:
            continue
        if RSIs[i] >= 70:

            resulting = backtestTrade.trade(candles[i],candles,RSIs,i,sl)
            results.append(resulting[0])
            z = resulting[1]

    return sumList(results)



##calcs sum of list###
def sumList(list):
    sum = 0
    for i in list:
        sum += i
    return sum





# prints results show in GranularityTestResults
print("Instrument \t Granularity \t Stop \t Daily Pips")
for instrument in instruments:
    for granularity in granularities:
        candles, RSIs = collectData(instrument, granularity[0], 5000)
        resultsList = []
        for i in range(10,51):
            stopLevel = i/10000
            results = trainAlgo(candles,RSIs,stopLevel)
            resultsList.append((stopLevel,results))

        bestStopTuple = max(resultsList, key = lambda x:x[1])
        dailyPips = (bestStopTuple[1]*10000)/(((granularity[1] * 5000)/60)/24)
        print(instrument + "\t" + granularity[0] + "\t" + str(bestStopTuple[0]) + "\t" + str(dailyPips))