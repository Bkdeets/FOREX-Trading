


def main(datapoints):

    prices = []
    for i in range(0,len(datapoints)):
        prices.append(float(datapoints[i]['mid']['c']))

    sma = sum(prices)/len(prices)

    return sma


