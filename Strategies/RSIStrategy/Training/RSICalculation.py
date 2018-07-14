
import requests
import json
import accountDetails



# ##Comment this block back out when finished###
# instrument = "EUR_GBP"
#
# ##Getting the historical candlestick data#####
# query = {
#     "granularity":"M15",
#     "count" : 1000
# }
#
# candleData = requests.get(accountDetails.baseURL + "instruments/" + instrument + "/candles", headers=accountDetails.headers, params=query)
#
# ##############################################
# ##Parsing json data##
# parsedData = json.loads(json.dumps(candleData.json()))
#
# ##Putting parsed data into a list of candles##
# candles = parsedData["candles"]
# ##############################################


##Calcs the RSI based on the candles list##
def calcRSI(period, candles):
    ##Initialize RSI
    RSI = []
    nah = initRS(period, candles)
    RS = nah[0]
    avgSog = nah[1]
    avgSol = nah[2]

    for i in range(1, len(candles)):
        change = float(candles[i]["mid"]["c"]) - float(candles[i - 1]["mid"]["c"])
        if i == 14:
            RSI.append(100 - (100 / (1 + RS)))
        elif i > 14:
            results = updateRSI(change,avgSog,avgSol)
            RSIVal = results[0]
            avgSog = results[1]
            avgSol = results[2]

            RSI.append(RSIVal)
        else:
            RSI.append(0)
    return RSI, avgSog, avgSol


##Initializes the RSI by the period##
def initRS(period, candles):
    gains = []
    losses = []

    for i in range(0, period):
        change = float(candles[i]["mid"]["c"]) - float(candles[i - 1]["mid"]["c"])

        if (change >= 0):
            gains.append(change)

        else:
            losses.append(-change)

    AvgSog = sumList(gains) / 14
    AvgSol = sumList(losses) / 14
    RS = AvgSog / AvgSol

    # print("XXXXXXXXXxxxxxxx")
    # print(AvgSog)
    # print(AvgSol)
    # print(RS)
    # print(100-(100/(1+RS)))
    # print("XXXXXXXXXxxxxxxx")

    sip = [RS, AvgSog, AvgSol, gains, losses]

    return sip


##############################################

##calcs sum of list###
def sumList(list):
    sum = 0
    for i in list:
        sum += i
    return sum


##Updates RSI with the next price level passed##
def updateRSI(priceChange, avgSog, avgSol):
    if priceChange > 0:
        avgSog = ((avgSog * 13) + priceChange) / 14
        avgSol = ((avgSol * 13) - 0) / 14
    elif priceChange < 0:
        avgSol = ((avgSol * 13) - priceChange) / 14
        avgSog = ((avgSog * 13) - 0) / 14

    if avgSol == 0:
        RS = 100
    else:
        RS = avgSog / avgSol

    RSI = 100 - (100 / (1 + RS))

    return [RSI, avgSog, avgSol]


# RSIs, avgsog,avgsol = calcRSI(14,candles)
#
# for ea in RSIs:
#     print(ea)
