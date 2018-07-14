## 3/11/2018 This training file is for a different idea on how to train the RSI Values. Not using at the moment



def train(candles,RSIs):
    results = []
    ##This range represents the RSI values to test (5 to 40) ##
    for x in range(70,101):

        stat = RSIStats.RSIStat()
        stat.setRSI(x)

        nCompz = []
        y = 15

        for i in range(15,len(RSIs)):


            if i < y:
                continue

            if x == int(RSIs[i]):

                n = 1
                while n < 2:

                    ##candles[i] = currentCandle, candles[i+n+1] = candle to get change of
                    try:
                        z = getChange(candles[i],candles[i+n])
                    except:
                        z = 0

                    nz = (n,z)

                    ##This will take the data from the nz instance and aggregate it into the masterlist nCompz##
                    nCompz = integrate(nCompz,nz)

                    n += 1
                y += n
        stat.nCompz = nCompz
        results.append(stat)

    return results

def integrate(tupList,tuple):
    key = tuple[0]
    value = tuple[1]

    isIn = False
    if len(tupList) == 0:
        tupList.append((key,[value]))
    for t in tupList:
        if key == t[0]:
            t[1].append(value)
            isIn = True
    if not isIn:
        tupList.append((key, [value]))

    return tupList

def getChange(candle1,candle2):
    startPrice = float(candle1["mid"]["c"])
    change = float(candle2["mid"]["c"])-startPrice
    return change

def trade(candle,candles,RSIs,i):
    entryPrice = float(candle["mid"]["c"])
    totalChange = 0


    for n in range(i,len(RSIs)):
        change = float(candles[n]["mid"]["c"])-entryPrice
        totalChange+=change
        pctPL = totalChange/entryPrice
        if pctPL > target:
            ##return [pctPL*100,n]
            ##return [pctPL*valOfTrade*leverage,n]
            return trailingStop(pctPL,entryPrice,n,RSIs,totalChange,candles)

        if pctPL < stop:
            return [pctPL,n]
            ##return [pctPL*100,n]

        if RSIs[n] >= 70:
            return [pctPL,n]
            ##return [pctPL*100,n]
    return [0,0]






##Main call################
def main():
    RSIs = calcRSI(14,candles)
    ##results = trainAlgo(candles,RSIs)
    results = trainRSI.train(candles,RSIs)
    masterCount = 0
    for RSIStat in results:
        print("RSI: " + str(RSIStat.getRSILevel()))

        for value in RSIStat.getnCompz():
            ##print("\t Candle number: " + str(value[0] + 1))
            ##print(value[0] + 1)
            total = 0
            count = 0
            for vz in value[1]:
                count +=1
                total += vz
                ##print(str(vz))
            ##print("Average: ")
            print(total/count)
            masterCount += count
        print("\n")
    print(masterCount)