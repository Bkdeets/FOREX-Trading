## Author: Britton K. Deets
## Created: July 14th , 2018


'''
This strategy will be a simple strategy for trading ma/price crossovers.
This will mostly be used as a very simple strategy to test the backtesting, forwardtesting, and production environments.
It would be cool to make a machine learning version where learned the patterns assoc with crossovers based
on an arbitrary number of ma's
'''

import math
from Strategies.MA import genSMA


def checkEntry(sma, datapoint, distance):
    close = float(datapoint['mid']['c'])
    actual_dist = (sma-close)/min(close,sma)
    if abs(actual_dist)-distance >= 0:
        if actual_dist > 0:
            return "enterLong"
        else:
            return "enterShort"
    return None


def checkExit(sma, datapoint, inLong):
    close = float(datapoint['mid']['c'])
    actual_distance = sma - close
    if inLong and actual_distance <= 0:
        return "exitLong"
    elif not inLong and actual_distance >= 0:
        return "exitShort"
    else:
        return None


def nextIndication(sma, isOpen, inLong, datapoint, distance):
    if isOpen:
        indication = checkExit(sma, datapoint, inLong)
    else:
        indication = checkEntry(sma, datapoint, distance)
    return indication


def main(datapoints, isOpen, inLong, strat_args):
    sma = genSMA.main(datapoints)
    indication = nextIndication(sma, isOpen, inLong, datapoints[-1], strat_args['distance'])
    return indication, sma

tradespecs = {
        "supportINTD": "True",
}