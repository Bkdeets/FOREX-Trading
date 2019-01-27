# FOREX-Trading

Trading application to interact with OANDA API and place trades based on predefined strategies.

Requires an acctDetails file for your OANDA trading account like:

    {
	  "token": "\"/YOUR TOKEN\"",
	  "accountID": "\"ACCT ID\"",
	  "baseURL": "https://api-fxtrade.oanda.com/v3/",
	  "headers": {
	    "Authorization":"Bearer YOUR TOKEN",
	    "Content-Type": "application/json"
	  }
	}
	
Currently only the Backtester works, not Production.

Backtester only has one strategy available based on a simple moving average. This strategy is just for 
making sure the Backtester works properly.