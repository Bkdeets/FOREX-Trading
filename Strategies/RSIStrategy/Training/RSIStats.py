##no computation will be done within this class, it just keeps data in the form I want##
class RSIStat:

    ##Variables#######
    RSILevel = 0

    ##This will be a list of tuples with n being candle # after entry candle 0, and z being price change of candle n
    nCompz = []

    ##################


    ##Constructor to set RSILevel##
    def RSIStats(self,RSI):
        self.RSILevel = RSI


    ##function to add a tuple to nCompZ###
    ##This will be under the assumption that the tuple sent will be the average of each RSILevel hit##
    def addToNZ(self,tuple):
        self.nCompZ.append(tuple)

    def getRSILevel(self):
        return self.RSILevel

    def setRSI(self,RSI):
        self.RSILevel = RSI

    def getnCompz(self):
        return self.nCompz