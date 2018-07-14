##This file will be tradeable on live##

import sys
import traceback
from Training import RSICalculation,trailingStopLevel
import requests
import json
import time
import emailer
import accountDetails
import datetime
from Backtesting import backtestStream
import countdown

def createQuery(granularity,count):
    ##granularities on http://developer.oanda.com/rest-live-v20/instrument-df/
    ## count is an int from 0 to 5000 inclusive
    query = {
        "granularity": granularity,
        "count": count
    }
    return query

def checkForOpen(instrument):
    positionsRaw = requests.get(accountDetails.getBaseURL() + "accounts/" + accountDetails.accountID + "/openPositions",headers=accountDetails.getHeaders())
    print(positionsRaw)
    parsedData = json.loads(json.dumps(positionsRaw.json()))
    positions = parsedData["positions"]
    for position in positions:
        if instrument == position["instrument"]:
            return [True,position["long"]["unrealizedPL"]]
    return [False,0]

instrument = input("Enter a currency pair: ")

##get data
candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles",
                          headers=accountDetails.getHeaders(), params=createQuery("M15", 500))
print(candleData)
##Parsing json data##
parsedData = json.loads(json.dumps(candleData.json()))
##Putting parsed data into a list of candles##
candles = parsedData["candles"]
#####Get current RSI#####
RSIs, avgSog, avgSol = RSICalculation.calcRSI(14, candles)
currentRSI = RSIs[-1]
bestStopFloat = float(backtestStream.getBestStop(candles, RSIs))
bestStopStr = "{0:.4f}".format(bestStopFloat)
rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/"+ instrument +"/candles", headers = accountDetails.getHeaders(), params = createQuery("M5",3))
parsedCandle = json.loads(json.dumps(rawCandle.json()))

##curentPrice is live price -- only using completed candles##
currentPrice1 = float(parsedCandle["candles"][2]["mid"]["c"])

takeProfitPrice = "{0:.4f}".format(bestStopFloat+currentPrice1)

mktOrderParamsTrailing = {
    "order": {
        "units": "1000",
        "instrument": instrument,
        "timeInForce": "FOK",
        "type": "MARKET",
        "positionFill": "DEFAULT",
        "takeProfitOnFill":{
            "price": "placeholder"
        },
        "stopLossOnFill": {
            "distance": bestStopStr
            }
        }
    }


##Stream data##
def stream(RSI,avgSog,avgSol):
    ## True so it will run indefinitely (until I cancel it running or something goes wrong) ##

    c = 0
    while True:
        if c != 0:
            ##get current price data
            rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/"+ instrument +"/candles", headers = accountDetails.getHeaders(), params = createQuery("M5",3))
            parsedCandle = json.loads(json.dumps(rawCandle.json()))

            ##curentPrice is live price -- only using completed candles##
            currentPrice = float(parsedCandle["candles"][2]["mid"]["c"])

            p1Price = float(parsedCandle["candles"][1]["mid"]["c"])
            p2Price = float(parsedCandle["candles"][0]["mid"]["c"])

            priceChange = p1Price-p2Price

            ##update RSI##
            results = RSICalculation.updateRSI(priceChange,avgSog,avgSol)
            RSI = results[0]
            avgSog = results[1]
            avgSol = results[2]

        print("Waiting for trade...")
        print(RSI)
        print("\n")

        if RSI >= 70:
            print("Opening trade...")
            openTradeTrailing(instrument)

        print("RSI update in 5 minutes: " + str(datetime.datetime.now()))

        time.sleep(60*5)
        c+=1


def openTradeTrailing(instrument):

    ##Current price chunk
    rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/" + instrument + "/candles",
                             headers=accountDetails.getHeaders(), params=createQuery("M5", 3))
    parsedCandle = json.loads(json.dumps(rawCandle.json()))

    ##curentPrice is live price -- only using completed candles##
    currentPrice1 = float(parsedCandle["candles"][2]["mid"]["c"])



    bestStopFloat = float(backtestStream.getBestStop(candles, RSIs))

    takeProfitPrice = "{0:.4f}".format(bestStopFloat + currentPrice1)

    mktOrderParamsTrailing["instrument"] = instrument
    mktOrderParamsTrailing["order"]["takeProfitOnFill"]["price"] = takeProfitPrice

    result = requests.post(accountDetails.getBaseURL() + "/accounts/" + accountDetails.accountID + "/orders", headers = accountDetails.getHeaders(), json = mktOrderParamsTrailing)
    print(result)

    print("Trade entered with the following parameters:")


    ##get entry price##
    resultBody = json.loads(json.dumps(result.json()))
    print(resultBody)
    entryPrice = float(resultBody["orderFillTransaction"]["price"])

    print("Entry price: " + str(entryPrice))
    print("Take Profit: " + str(float(resultBody["orderCreateTransaction"]["takeProfitOnFill"]["price"]) - entryPrice))
    print("Stop Loss: " + str(float(resultBody["orderCreateTransaction"]["stopLossOnFill"]["distance"])))

    ##get tradeId##
    tradeId = resultBody["orderFillTransaction"]["id"]


    tradeIsOpen = True

    currentTime = time.clock()
    exitTime = currentTime + 60
    emailer.sendEmail(instrument,entryPrice)
    while tradeIsOpen:
        time.sleep(400)
        tradeIsOpenA = checkForOpen(instrument)

        if not tradeIsOpenA[0]:
            tradeIsOpen = False
        else:
            print("Trade is open. PL: " + str(tradeIsOpenA[1]))



    print(result)

def getTradeStatus(tradeId):
    tradeStatus = requests.get(accountDetails.getBaseURL() + "accounts/" + accountDetails.accountID + "/trades/" + tradeId, headers = accountDetails.getHeaders())
    parsedStatus = json.loads(json.dumps(tradeStatus.json()))

    print(tradeStatus)
    if parsedStatus["trade"]["state"] == "OPEN":
        return True
    else:
        return False

def main():

    while True:

        try:
            open = checkForOpen(instrument)
            if open[0]:
                print("Open position. Waiting for 5 minutes.")
                print("PL: " + str(open[1]))
                time.sleep(60*5)
            else:
                try:
                    stream(currentRSI,avgSog,avgSol)
                except Exception as e:
                    print(e)
                    #print(traceback.format_exc())
                    #print(sys.exc_info()[0])
                    #print("Error occurred... Rerunning program in 5 minutes.")
                    time.sleep(60*5)
        except Exception as e:
            print(e)
            #print(traceback.format_exc())
            #print(sys.exc_info()[0])
            print("Error occurred... Rerunning program in 5 minutes.")
            time.sleep(60 * 5)

main()




