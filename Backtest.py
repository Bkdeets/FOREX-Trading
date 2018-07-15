## Author: Britton K. Deets
## Created: July 14th , 2018

from Strategies import *
import CollectData
import json


def long(specs, index):
    exe_price = rel_data[index]
    state = "L"
    result = [exe_price, state]
    return result

def short(specs, index):
    exe_price = rel_data[index]
    state = "S"
    result = [exe_price, state]
    return result

def exit_l(specs, index):
    exe_price = rel_data[index]
    state = None
    result = [exe_price, state]
    return result

def exit_s(specs, index):
    exe_price = rel_data[index]
    state = None
    result = [exe_price, state]
    return result



indictation_dict = {
    "L": long,
    "S": short,
    "EL": exit_l,
    "ES": exit_s
}



def trade(specs, indication, index, balances, state):


    balance = balances[-1]
    action = indictation_dict[indication]

    trade_data = action(specs, index)

    trade_data.append(balance)

    # [exe_price, state, balance]
    return trade_data


# Will always backtest on the largest period given by the granularity and period specified in strategy datareq
def backtest(strategy, granularity, instrument, strat_args):


    # Initializing variables
    state = None
    balance = 1000
    balances = [balance]
    trades = []
    studies = []
    specs = json.load(strategy.tradespecs)

    # Setting rel_data to global so trade functions can access it without creating new list each time
    global rel_data
    rel_data = CollectData.getData(specs['supportINTD'], granularity, instrument)

    # Starting backtest
    for index,datapoint in enumerate(rel_data):

        # Indication can be anything in indication dict or None (False)
        indication,study = strategy.main(rel_data, state, strat_args)

        if indication:
            studies.append(study)
            trade_res = trade(specs, indication, index, balances, state)
            balance = trade_res[-1]
            state = trade_res[1]
            balances.append(balance)
            trades.append(trade_res)


        else:
            studies.append(study)


    # Write file with all relevant results
    # Return nothing

