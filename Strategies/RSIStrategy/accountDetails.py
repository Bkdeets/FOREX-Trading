
import requests
import urllib

##account details for my v20 "Program" account


token = "de144cd39cd3bb6833aa4c5dc08a2e8f-47dbd14a6b9acac1ec3ba0275669fe82"
accountID = "001-001-603989-001"
baseURL = "https://api-fxtrade.oanda.com/v3/"
headers = {
    "Authorization":"Bearer de144cd39cd3bb6833aa4c5dc08a2e8f-47dbd14a6b9acac1ec3ba0275669fe82",
    "Content-Type": "application/json"
}


def getHeaders():
    return headers

def getBaseURL():
    return baseURL



