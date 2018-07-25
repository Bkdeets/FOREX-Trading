## Author: Britton K. Deets
## Created: July 14th , 2018

from Strategies import *
import xlsxwriter
import csv
import CollectData
import json
import matplotlib.pyplot as plt
import traceback


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


# Will always backtest on the largest time period given by the granularity and period specified in strategy datareq
def backtest(strategy, granularity, instrument, strat_args, plotThis=False):

    # Initializing variables
    state = None
    entry_pc = None
    balance = 10000
    balances = [balance]
    trades = []
    studies = []
    specs = strategy.tradespecs
    period = strat_args['period']
    trade_data = []

    # Setting rel_data to global so trade functions can access it without creating new list each time
    global rel_data
    rel_data = CollectData.getData(specs['supportINTD'], granularity, instrument)
    rel_data = rel_data['candles']

    # Starting backtest
    for index,datapoint in enumerate(rel_data):

        # Pulling the correct data to feed to the strategy
        if index >= period:
            relDataChunk = rel_data[index-period:index]
        elif index == 0:
            relDataChunk = [rel_data[0]]
        else:
            relDataChunk = rel_data[0:index]

        # Indication can be anything in indication dict or None (False)
        indication,study = strategy.main(relDataChunk, state, strat_args)

        if indication:

            studies.append(study)
            trade_data = trade(indication, index, balances, entry_pc)
            balance = trade_data[-1]
            state = trade_data[1]
            entry_pc = trade_data[0]
            balances.append(balance)
            trade_data.append(index)
            trades.append(trade_data)

        else:
            studies.append(study)


    closes = []
    for c in rel_data:
        closes.append(float(c['mid']['c']))

    return balances,len(rel_data), rel_data, trades


strat_args = {
    'period':100,
    'distance':.005
}
currency = "EUR_USD"
granularity = "D"
from Strategies.MA import strategy


balances, numCandles, candles, tradeData = backtest(strategy, granularity, currency, strat_args, plotThis=True)


### In a display file ###

## Want to see plot of the trades
## Want to see plot of the balances
## Want to see trade data
## Descriptive statistics

### Should I do this with a front-end application????????????????? ###