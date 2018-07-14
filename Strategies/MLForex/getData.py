import time
import sys
import traceback
import requests
import json
import matplotlib.pyplot as plt
import accountDetails
import datetime
import numpy
import pprint
import pandas


granularity = [("M1",1)]
instruments = ["EUR_USD","EUR_GBP","USD_CHF","NZD_USD","GBP_USD","USD_CAD"]


def createQueryTime(granularity,fromTime,toTime):
    query = {
        "granularity": granularity,
        "from":fromTime,
        "to": toTime
    }
    return query


def collectDataTime(instrument,granularity,fromTime,toTime):

    fromTime = str(fromTime.isoformat("T")) + "Z"
    toTime = str(toTime.isoformat("T")) + "Z"
    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles",
                              headers=accountDetails.getHeaders(),
                              params=createQueryTime(granularity,fromTime,toTime))
    parsedData = json.loads(json.dumps(candleData.json()))
    #print(parsedData)
    candles = parsedData["candles"]
    return candles



def createQueryCount(granularity, count):
    query = {
        "granularity": granularity,
        "count":count
    }
    return query



def collectDataCount(instrument,granularity,count):

    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles",
                              headers=accountDetails.getHeaders(),
                              params=createQueryCount(granularity,count))
    parsedData = json.loads(json.dumps(candleData.json()))
    candles = parsedData["candles"]

    prices = []
    volumes = []
    for candle in candles:
        prices.append(float(candle['mid']['c']))
        volumes.append(float(candle['volume']))
    return prices,volumes


def calcSMADist(length, aList):
    smas = []

    for i in range(0,len(aList)):

        period = aList[i:length+i]
        avg = sum(period)/len(period)

        dist = (aList[i]-avg)/avg
        smas.append(dist)

    return smas


def main():
    prices,volumes = collectDataCount("EUR_USD","D",1000)
    sma_p = calcSMADist(5,prices)
    sma_v = calcSMADist(5,volumes)

    price_changes = []
    for i in range(0,len(prices)):
        try:
            change = (prices[i]-prices[i-1])/prices[i-1]
        except:
            change = 0
        price_changes.append(change)


    price_binary = ["Up" if x > 0 else "Down" for x in price_changes]

    dictionary = {'sma_price':sma_p,'sma_volume':sma_v,'xisUp':price_binary}

    dataset = pandas.DataFrame(dictionary)

    dataset = dataset[:-1]
    return dataset