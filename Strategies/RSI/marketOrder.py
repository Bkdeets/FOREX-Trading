import requests
import urllib
import json

import accountDetails
from Training import trailingStopLevel


token = "de144cd39cd3bb6833aa4c5dc08a2e8f-47dbd14a6b9acac1ec3ba0275669fe82"
accountID = "001-001-603989-001"

baseURL = "https://api-fxtrade.oanda.com/v3/accounts/"

headers = {
    "Authorization":"Bearer de144cd39cd3bb6833aa4c5dc08a2e8f-47dbd14a6b9acac1ec3ba0275669fe82",
    "Content-Type": "application/json"
}
query = {
    "granularity":"H1",
    "count" : 5000
}

def createQuery(granularity,count):
    ##granularities on http://developer.oanda.com/rest-live-v20/instrument-df/
    ## count is an int from 0 to 5000 inclusive
    query = {
        "granularity": granularity,
        "count": count
    }
    return query


instrument = "EUR_USD"
candleData = requests.get(accountDetails.getBaseURL() + "instruments/" + instrument + "/candles", headers=accountDetails.getHeaders(), params=query)
parsedData = json.loads(json.dumps(candleData.json()))
candles = parsedData["candles"]


rawCandle = requests.get(accountDetails.getBaseURL() + "/instruments/"+ instrument +"/candles", headers = accountDetails.getHeaders(), params = createQuery("M5",3))
parsedCandle = json.loads(json.dumps(rawCandle.json()))

##curentPrice is live price -- only using completed candles##
currentPrice1 = float(parsedCandle["candles"][2]["mid"]["c"])



mktOrderParamsTrailing = {
    "order": {
        "units": "800",
        "instrument": instrument,
        "timeInForce": "FOK",
        "type": "MARKET",
        "positionFill": "DEFAULT",
        "takeProfitOnFill":{
            "price": "{0:.4f}".format(.0011+currentPrice1)
        },
        "stopLossOnFill": {
            "distance": ".0011"
            }
        }
    }



post = requests.post(baseURL+accountID+"/orders",headers=headers,json=orderConf)

print("POST:")
print(post)
print(post.headers)
print(post.text)




