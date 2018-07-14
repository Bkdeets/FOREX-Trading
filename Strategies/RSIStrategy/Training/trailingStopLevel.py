## The purpose of this file is to calculate the most optimal trailing stop loss level

## 1. Calc Average range of candle changes
## 2. Add one sd to the average change so we know that 15.8% of the time the stop will be hit.



import statistics

import math
import requests
import json
import accountDetails



instrument = "EUR_USD"
query = {
    "granularity":"M15",
    "count" : 1000
}

candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles", headers=accountDetails.getHeaders(), params=query)
parsedData = json.loads(json.dumps(candleData.json()))
candles = parsedData["candles"]


def candleChanges(candles):
    candleChangeList = []
    for i in range(1,len(candles)):
        change = float(candles[i]["mid"]["h"]) - float(candles[i]["mid"]["l"])
        candleChangeList.append(change)
    return candleChangeList




def main(candles):

    ##list of changes
    changesList = candleChanges(candles)

    standardDeviation = statistics.stdev(changesList)

    mean = math.fabs(statistics.mean(changesList))

    stopLevel = mean + standardDeviation

    # print("Mean:")
    # print(mean)
    # print("SD:")
    # print(standardDeviation)
    # print("Median:")
    # print(median)
    # print("Stop Level:")
    # print(stopLevel)

    return mean,standardDeviation


main(candles)