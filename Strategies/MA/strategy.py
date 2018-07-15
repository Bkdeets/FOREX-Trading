## Author: Britton K. Deets
## Created: July 14th , 2018


'''
This strategy will be a simple strategy for trading ma/price crossovers.
This will mostly be used as a very simple strategy to test the backtesting, forwardtesting, and production environments.
It would be cool to make a maching learning version where learned the patterns assoc with crossovers based
    on an arbitrary number of ma's
'''

import math
import genSMA



def checkEntry(sma, datapoint, distance):
    close = float(datapoint['c'])
    actual_dist = (sma-close)/close
    if abs(actual_dist)-distance >= 0:
        if actual_dist < 0:
            return "L"
        else:
            return "S"

    return None



def checkExit(sma, datapoint, state):

    close = float(datapoint['c'])
    actual_distance = sma - close
    if state == "L":
        if actual_distance >= 0:
            return "EL"
        else:
            return "L"
    elif state == "S":
        if actual_distance <= 0:
            return "ES"
        else:
            return "S"




def nextIndication(sma, state, datapoint, distance):
    if state:
        indication = checkExit(sma, datapoint, state)
    else:
        indication = checkEntry(sma, datapoint, distance)
    return indication


def main(datapoints, state, strat_args):

    period = strat_args['period']
    distance = strat_args['distance']

    sma = genSMA.main(datapoints, period)

    indication = nextIndication(sma, state, datapoints[-1], distance)

    return indication, sma