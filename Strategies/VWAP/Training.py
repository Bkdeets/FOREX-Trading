
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

# get oanda data


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
    return candles