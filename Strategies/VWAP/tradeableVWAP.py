
import time
import sys
import traceback
import requests
import json
import matplotlib.pyplot as plt
import accountDetails
import CalcVWAP
import datetime
import numpy
import sys
import traceback
import emailer


instrument = input("Enter a currency pair: ")
def getCurrentPrice(instrument,long=False,short=False):
    query = {
        "granularity": "M1",
        "count": 2
    }

    rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/" + instrument + "/candles",
                             headers=accountDetails.getHeaders(), params=query)
    parsedCandle = json.loads(json.dumps(rawCandle.json()))

    ##curentPrice is live price -- only using completed candles##
    currentPrice1 = float(parsedCandle["candles"][-1]["mid"]["c"])

    if long:
        cp = float(parsedCandle["candles"][-1][""]["c"])

    return "{0:.4f}".format(currentPrice1)

# Can be used as long entry or short exit
long_params = {
    "order": {
        "units": "1000",
        "instrument": instrument,
        "timeInForce": "GTD",
        "type": "LIMIT",
        "price": "willcauseerror",
        "positionFill": "DEFAULT",
        }
    }

long_params_exit = {
    "order": {
        "units": "-1000",
        "instrument": instrument,
        "timeInForce": "FOK",
        "type": "MARKET",
        "gtdTime": "Error",
        "positionFill": "DEFAULT",
        }
    }

# Can be used as short entry or long exit
short_params = {
    "order": {
        "units": "-1000",
        "instrument": instrument,
        "timeInForce": "GTD",
        "type": "LIMIT",
        "price": "willcauseerror",
        "gtdTime": "Error",
        "positionFill": "DEFAULT",
        }
    }

short_params_exit = {
    "order": {
        "units": "1000",
        "instrument": instrument,
        "timeInForce": "FOK",
        "type": "MARKET",
        "positionFill": "DEFAULT",
        }
    }


def createQuery(granularity,count):
    query = {
        "granularity": granularity,
        "count": count
    }
    return query

def createTimeQuery(granularity,fromTime,toTime):
    query = {
        "granularity": granularity,
        "from":fromTime,
        "to": toTime
    }
    return query

def checkForOpen(instrument):
    positionsRaw = requests.get(accountDetails.getBaseURL() + "accounts/" + accountDetails.accountID + "/openPositions", headers=accountDetails.getHeaders())
    print(positionsRaw)
    parsedData = json.loads(json.dumps(positionsRaw.json()))
    positions = parsedData["positions"]
    for position in positions:
        if instrument == position["instrument"]:
            return [True,position["long"]["unrealizedPL"]]
    return [False,0]


def collectData(instrument,granularity,fromTime,toTime):
    candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles", headers=accountDetails.getHeaders(), params=createTimeQuery(granularity,fromTime,toTime))
    print(candleData)
    parsedData = json.loads(json.dumps(candleData.json()))
    candles = parsedData["candles"]
    #print(candles)
    return candles


def calcVWAPs(candles):
    VWAP_Price = []
    candleCloses = []
    VWAPs = []
    v_dist_from_price = []
    totalV = 0
    totalVP = 0
    for candle in candles:
        #print(candle)
        candleClose = float(candle["mid"]["c"])
        tempAvg = (float(candle["mid"]["o"]) + float(candle["mid"]["l"]) + float(candle["mid"]["h"]) + float(candle["mid"]["c"]))/4
        VP = tempAvg * candle["volume"]

        totalV += candle["volume"]
        totalVP += VP

        VWAP = totalVP/totalV

        VWAPs.append(VWAP)
        v_dist_from_price.append(abs((candleClose-VWAP)/VWAP)) # %dist from vwap
        candleCloses.append(candleClose)


    for n in range(len(candleCloses)):
        vprice = (candleCloses[n],VWAPs[n])
        VWAP_Price.append(vprice)

    # VWAP_Price looks like [(price,vwap),(price1,vwap1),...)
    return VWAP_Price,v_dist_from_price

def checkForOrder(instrument):
    ordersRaw = requests.get(accountDetails.getBaseURL() + "accounts/" + accountDetails.accountID + "/orders?instrument="+instrument,
                                headers=accountDetails.getHeaders())
    print(ordersRaw)
    parsedData = json.loads(json.dumps(ordersRaw.json()))
    orders = parsedData["orders"]
    if len(orders) > 0:
        return True

    return False

def open_trade(instrument, params):

    try:
        result = requests.post(accountDetails.getBaseURL() + "/accounts/" + accountDetails.accountID + "/orders",
                               headers=accountDetails.getHeaders(), json=params)
        resultBody = json.loads(json.dumps(result.json()))

        print(resultBody)
        entryPrice = float(resultBody["orderFillTransaction"]["price"])

        emailer.sendEmail(instrument,entryPrice)
        print("Entry price: " + str(entryPrice))

    except:
        print("Unable to enter trade...")
        traceback.print_exc()


##Stream data##
def stream(instrument,vwaps,vdists,candles):
    ## True so it will run indefinitely (until I cancel it running or something goes wrong) ##

    p_with_v = vwaps
    dist_from_price = vdists
    vwaps = []
    c = 0
    currentPrice = float(candles[-1]['mid']['c'])
    long_o = False
    short_o = False
    while True:
        if c != 0:
            ##get current price data
            rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/" + instrument + "/candles",
                                     headers = accountDetails.getHeaders(), params = createQuery("M1", 3))
            parsedCandle = json.loads(json.dumps(rawCandle.json()))

            candle = parsedCandle["candles"][1]
            candles.append(candle)

            p_with_v, dist_from_price = calcVWAPs(candles)


        print("Waiting for trade...")
        #print("VWAP:", p_with_v[-1][-1], "Price:", p_with_v[-1][0])
        #print("\n")

        price = p_with_v[-1][0]
        vwap = p_with_v[-1][-1]
        distance = (price - vwap) / price
        level = numpy.std(dist_from_price) * 3
        #print("Distance: ", abs(distance), " Level: ", level)
        tradeIsOn = checkForOpen(instrument)
        isOpen = tradeIsOn[0]


        long_entry_cond = abs(distance) > level and not isOpen and distance < 0
        short_entry_cond = abs(distance) > level and not isOpen and distance > 0
        open_order = checkForOrder(instrument)

        if not isOpen:

            if not open_order:
                if long_entry_cond:
                    long_params["price"] = getCurrentPrice(instrument)
                    end = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                    gtd = str(end.isoformat("T")) + "Z"
                    long_params["gtdTime"] = gtd
                    exe_price = open_trade(instrument,long_params)
                    long_o = True
                    print("Long ordered")

                elif short_entry_cond:
                    short_params["price"] = getCurrentPrice(instrument)
                    end = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                    gtd = str(end.isoformat("T")) + "Z"
                    short_params["gtdTime"] = gtd
                    exe_price = open_trade(instrument,short_params)
                    short_o = True
                    print("Short ordered")

        elif isOpen:
            long_exit_cond = vwap >= price
            short_exit_cond = vwap <= price

            if long_exit_cond:
                exe_price = open_trade(instrument,short_params)
                print("Long closed at: ",exe_price)
                long_o = False
            elif short_exit_cond:
                exe_price = open_trade(instrument,long_params)
                print("Short closed at: ", exe_price)
                short_o = False

        current_time = datetime.datetime.time(datetime.datetime.now())
        if current_time > datetime.time(hour=0, minute=0, second=0, microsecond=0) and current_time < datetime.time(hour=0, minute=2, second=0, microsecond=0):
            if tradeIsOn[0]:
                if long_o:
                    exe_price = open_trade(instrument, short_params_exit)
                    print("Long closed")
                    long_o = False
                elif short_o:
                    exe_price = open_trade(instrument, long_params_exit)
                    print("Short closed")
                    short_o = False


        print("VWAP update in 1 minute: " + str(datetime.datetime.now()))

        time.sleep(60)
        c+=1

def getTimes():
    end = str(datetime.datetime.utcnow().isoformat("T")) + "Z"
    start = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    start = str(start.isoformat("T")) + "Z"
    return start,end


def main(instrument):

    while True:

        try:
            start,end = getTimes()
            candles = collectData(instrument, "M1", start, end)
            vwaps,vdists = calcVWAPs(candles)
            open = checkForOpen(instrument)

            if open[0]:
                print("Open position. Waiting for 60 sec.")
                print("PL: " + str(open[1]))
                time.sleep(60)

            else:
                try:
                    stream(instrument,vwaps,vdists,candles)

                except Exception as e:
                    print(e)
                    print("Error occurred... Rerunning program in 60 sec.")
                    traceback.print_exc()
                    time.sleep(60)

        except Exception as e:
            print(e)
            print("Error occurred... Rerunning program in 60 sec.")
            traceback.print_exc()
            time.sleep(60)

main(instrument)
