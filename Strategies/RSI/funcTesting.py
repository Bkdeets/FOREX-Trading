from Backtesting import backtestStream
import requests
import accountDetails
import json
from Training import RSICalculation


# ##Comment this block back out when finished###
instrument = "GBP_USD"

##Getting the historical candlestick data#####
query = {
    "granularity":"M15",
    "count" : 1000
}

candleData = requests.get(accountDetails.baseURL + "instruments/" + instrument + "/candles", headers=accountDetails.headers, params=query)


##############################################
##Parsing json data##
parsedData = json.loads(json.dumps(candleData.json()))

##Putting parsed data into a list of candles##
candles = parsedData["candles"]
RSIs, avgSog, avgSol = RSICalculation.calcRSI(14, candles)
# ##############################################

bestStop = backtestStream.getBestStop(candles, RSIs)

print(type(bestStop))
print(type(float(bestStop)))
print(type("{0:.4f}".format(float(bestStop))))


