

class Trade:
    isOpen = False
    isLong = False
    isWin = False
    entryPrice = None
    exitPrice = None
    startIndex = 0
    endIndex = 0
    pctChange = 0


    def __init__(self, startIndex, endIndex=0, isOpen=False, isLong=False, entryPrice=None, exitPrice=None):
        self.isOpen = isOpen
        self.isLong = isLong
        self.entryPrice = entryPrice
        self.exitPrice = exitPrice
        self.startIndex = startIndex
        self.endIndex = endIndex

    def setIsOpen(self,booleanValue):
        self.isOpen = booleanValue

    def getIsOpen(self):
        return self.isOpen

    def setIsLong(self,booleanValue):
        self.isLong = booleanValue

    def getIsLong(self):
        return self.isLong

    def setEntryPrice(self,doubleValue):
        self.entryPrice = doubleValue

    def getEntryPrice(self):
        return self.entryPrice

    def setExitPrice(self,doubleValue):
        self.exitPrice = doubleValue

    def getExitPrice(self):
        return self.exitPrice

    def setStartIndex(self,index):
        self.startIndex = index

    def getStartIndex(self):
        return self.startIndex

    def setEndIndex(self,index):
        self.endIndex = index

    def getEndIndex(self):
        return self.endIndex

    def initPctChange(self):
        if self.exitPrice:
            self.pctChange = (self.exitPrice-self.entryPrice)/self.entryPrice

    def getPctChange(self):
        return self.pctChange

    def initIsWin(self):
        if not self.isOpen:
            if self.isLong and self.pctChange > 0:
                self.isWin = True
            elif not self.isLong and self.pctChange < 0:
                self.isWin = True
            else:
                self.isWin = False

    def getIsWin(self):
        return self.isWin

    def exitProcedures(self, index, exitPrice):
        self.setExitPrice(exitPrice)
        self.setEndIndex(index)
        self.initPctChange()
        self.setIsOpen(False)
        self.initIsWin()

    def entryProcedures(self, index, entryPrice, isLong):
        self.setStartIndex(index)
        self.setEntryPrice(entryPrice)
        self.setIsLong(isLong)
        self.setIsOpen(True)

    def toList(self):

        output = []

        if self.isLong:
            output.append("Long")
        else:
            output.append("Short")

        if self.isWin:
            output.append("Win")
        else:
            output.append("Loss")

        output.append(self.entryPrice)
        output.append(self.exitPrice)
        output.append(self.pctChange)
        output.append(self.startIndex)
        output.append(self.endIndex)
        output.append(self.isOpen)

        return output


