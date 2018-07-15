


def main(datapoints, period):

    rel_data = datapoints[-period:]
    sma = sum(rel_data)/len(rel_data)

    return sma


