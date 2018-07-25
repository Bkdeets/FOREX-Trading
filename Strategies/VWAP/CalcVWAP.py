
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


granularity = [("M1",1)]
instruments = ["EUR_USD","EUR_GBP","USD_CHF","NZD_USD","GBP_USD","USD_CAD"]

def plotter2(aList,aList2,instrument):
    plt.ioff()
    plt.title(instrument)
    plt.plot(aList)
    plt.plot(aList2)
    plt.show()

def plotter(aList,level,instrument):
    plt.title(str(-level) + " - " + instrument)
    plt.ioff()
    plt.plot(aList)
    plt.show()

def createQuery(granularity,fromTime,toTime):
    query = {
        "granularity": granularity,
        "from":fromTime,
        "to": toTime
    }
    return query

def collectData(instrument,granularity,fromTime,toTime):

    fromTime = str(fromTime.isoformat("T")) + "Z"
    toTime = str(toTime.isoformat("T")) + "Z"
    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles",
                              headers=accountDetails.getHeaders(),
                              params=createQuery(granularity,fromTime,toTime))
    parsedData = json.loads(json.dumps(candleData.json()))
    #print(parsedData)
    candles = parsedData["candles"]
    return candles

def calcVWAPs(candles):
    VWAP_Price = []
    candleCloses = []
    VWAPs = []
    v_dist_from_price = []
    totalV = 0
    totalVP = 0
    for candle in candles:
        candleClose = float(candle["mid"]["c"])
        tempAvg = (float(candle["mid"]["o"]) + float(candle["mid"]["l"]) + float(candle["mid"]["h"]) + float(candle["mid"]["c"]))/4
        VP = tempAvg * candle["volume"]

        totalV += candle["volume"]
        totalVP += VP

        VWAP = totalVP/totalV

        VWAPs.append(VWAP)
        v_dist_from_price.append(abs((candleClose-VWAP)/VWAP)) # %dist from vwap
        candleCloses.append(candleClose)

    #plotter2(VWAPs,candleCloses,"EUR_USD")

    for n in range(len(candleCloses)):
        vprice = (candleCloses[n],VWAPs[n])
        VWAP_Price.append(vprice)

    return VWAP_Price,v_dist_from_price

def calcVWAPs_backtest(candles):
    bt_dict = {}
    VWAP_Price = []
    VWAPs = []
    v_dist_from_price = []
    totalV = 0
    totalVP = 0
    i = 0
    for candle in candles:
        bt_dict[i] = {}

        candleClose = float(candle["mid"]["c"])
        tempAvg = (float(candle["mid"]["o"]) + float(candle["mid"]["l"]) + float(candle["mid"]["h"]) + float(candle["mid"]["c"]))/4
        VP = tempAvg * candle["volume"]

        totalV += candle["volume"]
        totalVP += VP

        VWAP = totalVP/totalV

        bt_dict[i]['VWAP'] = VWAP
        bt_dict[i]['Price'] = candleClose
        i += 1

    return bt_dict

def tradeVWAP(vWps,balance,units,leverage,testingLevel,instrument):



    plt.ioff()

    vs = []
    ps = []
    for v in vWps:
        ps.append(v[0])
        vs.append(v[1])

    plt.plot(vs)
    plt.plot(ps)



    balanceList = [balance]
    tradeValue = 0
    tradeIsOn = False
    long = False
    i = 0
    for t in vWps:

        #print(t[0]['mid']['c'])
        price = t[0]
        vwap = t[1]

        #if negative then price is below vwap
        positivity = price - vwap
        distance = positivity/price

        #print("Distance: ",distance)
        #print("Testing Level: ",testingLevel)

        ## Long Entry ##
        if abs(distance) > testingLevel and not tradeIsOn and distance < 0:
            tradeValue = price * units * leverage
            tradeIsOn = True
            long = True
            plt.plot(i,price,"bo")

        ## Long Exit ##
        elif tradeIsOn and vwap <= price and long:
            endingVal = units * price * leverage
            change = endingVal - tradeValue
            balance += change
            balanceList.append(balance)
            tradeIsOn = False
            long = False
            plt.plot(i, price, "r+")


        ## Short Entry ##
        if abs(distance) > testingLevel and not tradeIsOn and distance > 0:
            tradeValue = price * units * leverage
            tradeIsOn = True
            long = False
            plt.plot(i, price, "bo")

        ## Short Exit ##
        elif tradeIsOn and vwap >= price and not long:
            endingVal = units * price * leverage
            change = tradeValue - endingVal
            balance += change
            balanceList.append(balance)
            tradeIsOn = False
            long = True
            plt.plot(i, price, "r+")

        i += 1

    if tradeIsOn:
        if long:
            endingVal = units * price * leverage
            change = endingVal - tradeValue
            balance += change

        else:
            endingVal = units * price * leverage
            change = tradeValue - endingVal
            balance += change

        balanceList.append(balance)
        plt.plot(i, price, "r+")




    plt.title(str(testingLevel) + " - " + instrument + " - " + str(((balanceList[-1]-600)/600)*100) + " - " + str(balanceList[-1]))
    #plt.show()
    return balanceList

def sumList(list):
    sum = 0
    for i in list:
        sum += i
    return sum

def getBestLevels(instrument):
    end = datetime.datetime.utcnow()
    monthGain = []
    for i in range(0,6):
        start = end - datetime.timedelta(days=1)

        #print(end)
        try:
            candles = collectData(instrument, "M1", start, end)

            end = start
            vWp = calcVWAPs(candles)
            for i in range(1, 10, 1):
                level = i / 10000
                results = tradeVWAP(vWp, 600, 1000, 1, -level)
                monthGain.append((results,level))

        except:
            end = start
            continue

    res_dict = {}
    for list in monthGain:
        final = list[0][-1]
        if list[-1] not in res_dict:
            res_dict[list[-1]] = []

        res_dict[list[-1]].append(final)

    win_sl = 1/10000
    best = 0
    for key,value in res_dict.items():
        avg =  numpy.mean(value)
        #print(key, avg)
        if avg > best:
            best = avg

            win_sl = float(key)

    return win_sl

def backtest():
    print("Instrument \t End Balance \t Num Trades \t Level \t VOR" )
    end = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    orig_end = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    for instrument in instruments:
        #print(instrument)
        monthGain = []
        for i in range(0,6):
            start = end - datetime.timedelta(days=1)
            #print(end)
            try:
                candles = collectData(instrument, "M1", start, end)
                #print(candles)

                end = start
                V_with_price,v_dist = calcVWAPs(candles)

                sd_level = numpy.std(v_dist)
                #print(sd_level)
                for i in range(1, 4):

                    level = sd_level * i
                    results = tradeVWAP(V_with_price, 600, 1000, 1, level, instrument)

                    #print("SD: ",level)
                    #print("At ",i," SD:",results[-1])

                    closes = []
                    for c in candles:
                        #print(c['mid']['c'])
                        closes.append(float(c['mid']['c']))
                    print(V_with_price)
                    plotter2(V_with_price,closes,instrument)
                    monthGain.append((results,level))

            except Exception as e:
                print(e)
                end = start
                i+=1
                continue

        #print(instrument)
        i = 0

        for month in monthGain:
            le = month[0]
            lvl = month[-1]
            num_trades = len(le)
            tmp_var = []
            for trade in le:
                tmp_var.append(trade-600)
            var_returns = numpy.std(tmp_var)
            print(instrument, "\t", month[0][-1], "\t", len(le), "\t", lvl, "\t", var_returns)
            #plotter(month[0],month[-1],instrument)



        end = orig_end

#backtest(str(datetime.datetime.utcnow().isoformat("T")) + "Z")
# end = datetime.datetime.utcnow() - datetime.timedelta(days=1)
backtest()

#print(getBestLevels("EUR_USD"))