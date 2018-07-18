## Author: Britton K. Deets
## Created: July 14th , 2018

from Strategies import *
import xlsxwriter
import csv
import CollectData
import json
import matplotlib.pyplot as plt


def long(index):
    exe_price = float(rel_data[index]['mid']['c'])+.0002
    state = "L"
    result = [exe_price, state]
    return result

def short(index):
    exe_price = float(rel_data[index]['mid']['c'])-.0002
    state = "S"
    result = [exe_price, state]
    return result

def exit_l(index):
    exe_price = float(rel_data[index]['mid']['c'])-.0002
    state = None
    result = [exe_price, state]
    return result

def exit_s(index):
    exe_price = float(rel_data[index]['mid']['c'])+.0002
    state = None
    result = [exe_price, state]
    return result



indictation_dict = {
    "L": long,
    "S": short,
    "EL": exit_l,
    "ES": exit_s
}



def trade(indication, index, balances, entry_pc):


    balance = balances[-1]
    action = indictation_dict[indication]
    trade_data = action(index)

    pct_chg = False
    if indication.startswith("E"):
        pct_chg = (trade_data[0] - entry_pc) / entry_pc
        if indication == "ES":
            pct_chg = -pct_chg


    if pct_chg:
        balance = balance * (1+pct_chg)

    trade_data.append(pct_chg)
    trade_data.append(balance)

    # [exe_price, state, change, balance]
    return trade_data


# Will always backtest on the largest period given by the granularity and period specified in strategy datareq
def backtest(strategy, granularity, instrument, strat_args):


    # Initializing variables
    state = None
    entry_pc = None
    balance = 1000
    balances = [balance]
    trades = []
    studies = []
    specs = strategy.tradespecs
    period = strat_args['period']

    # Setting rel_data to global so trade functions can access it without creating new list each time
    global rel_data
    rel_data = CollectData.getData(specs['supportINTD'], granularity, instrument)
    rel_data = rel_data['candles']
    # Starting backtest
    for index,datapoint in enumerate(rel_data):

        # Indication can be anything in indication dict or None (False)
        indication,study = strategy.main(rel_data[index:index+period], state, strat_args)

        if indication:

            studies.append(study)
            trade_data = trade(indication, index, balances, entry_pc)
            balance = trade_data[-1]
            state = trade_data[1]
            entry_pc = trade_data[0]
            balances.append(balance)
            trades.append(trade_data)


        else:
            studies.append(study)

    # #balances =
    # plt.plot([bal[-1] for bal in trades])
    # plt.show()
    #
    # print(balance)
    # print(trades)
    # plt.plot(studies)
    # plt.show()
    # print(studies)
    return balances,len(rel_data)


strat_args = {
    'period':20,
    'distance':.0001
}

currencies = ["EUR_USD","EUR_GBP","USD_CHF","NZD_USD","GBP_USD","USD_CAD"]

###These are the only profitable time frames
granularities = ["H1","H4","D"]
distances = []
#periods = [10,20,50]
periods = [10]
for i in range(1,10):
    for zeros in range(3,6):
        zeros = "".join(['1','0'*zeros])
        dist = i/float(zeros)
        distances.append(dist)
from Strategies.MA import strategy
print(["Currency","Gran","Dist","Period","Ending","Min","Max","Trades"])
with open("output.csv","w+", newline='') as file:
    spamwriter = csv.writer(file, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Currency","Gran","Dist","Period","Ending","Min","Max","Trades","Daily Ret"])
    for currency in currencies:
        for granularity in granularities:
            for distance in distances:
                strat_args['distance'] = distance
                for period in periods:
                    strat_args['period'] = period
                    try:
                        balances,numCandles = backtest(strategy,granularity,currency,strat_args)
                    except:
                        balances = ["Connection error"]
                        numCandles = 1

                    pctRet = (balances[-1]-1000)/1000

                    if len(granularity) > 1:
                        num = int(granularity[1:])
                        if granularity[0] == "H":
                            days = (num*numCandles)/24
                        else:
                            days = (num*numCandles)/(24*60)
                    else:
                        days = numCandles

                    dailyRet = pctRet/days



                    line = [currency,granularity,distance,period,balances[-1],min(balances),max(balances),len(balances)-1,dailyRet]
                    spamwriter.writerow(line)
                    print(line)
