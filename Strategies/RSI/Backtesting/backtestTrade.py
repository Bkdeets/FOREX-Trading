from Training import trailingStopLevel

##Trailing stop
def trade(candle,candles,RSIs,i,stopLevel):
    entryPrice = float(candle["mid"]["c"])
    recentHigh = entryPrice

    for n in range(i,len(RSIs)):
        currentLow = float(candles[n]["mid"]["l"])
        change = currentLow-entryPrice
        if currentLow < recentHigh-float(stopLevel):
            ##returns the pl in pips
            ##print("Return: " + str(change))
            return [change,n]
        elif float(candles[n]["mid"]["h"]) > recentHigh:
            recentHigh = float(candles[n]["mid"]["h"])
    return [0,0]


##This is worst case scenario (assumes stop loss hit first
def tradeTpSlW(candle,candles,RSIs,i,tp,sl):
    entryPrice = float(candle["mid"]["c"])
    hardStop = entryPrice-float(sl)
    hardProfit = entryPrice+float(tp)

    for n in range(i,len(RSIs)):
        currentLow = float(candles[n]["mid"]["l"])
        currentHigh = float(candles[n]["mid"]["h"])
        if currentLow < hardStop:
            ##returns the pl in pips
            ##print("Return: " + str(change))
            return [-sl,n]
        elif currentHigh > hardProfit:
            return [tp,n]
    return [0,0]


##This is best case scenario (assumes pt hit 1st)
def tradeTpSlB(candle,candles,RSIs,i,tp,sl):
    entryPrice = float(candle["mid"]["c"])
    hardStop = entryPrice - float(sl)
    hardProfit = entryPrice + float(tp)

    for n in range(i, len(RSIs)):
        currentLow = float(candles[n]["mid"]["l"])
        currentHigh = float(candles[n]["mid"]["h"])
        if currentHigh > hardProfit:
            ##returns the pl in pips
            ##print("Return: " + str(change))
            return [tp, n]
        elif currentLow < hardStop:
            return [sl, n]
    return [0, 0]