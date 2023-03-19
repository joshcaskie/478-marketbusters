# region imports
from AlgorithmImports import *
from QuantConnect.DataSource import *
from QuantConnect.Data.UniverseSelection import *
# endregion
from datetime import datetime, timedelta
from collections import deque

from config import Config

class BenchmarkAlgo(QCAlgorithm):

    def Initialize(self):

        self.SetCash(Config.CASH)  
        self.SetStartDate(Config.START_DATE)
        self.SetEndDate(Config.END_DATE)

        # Set Account to Liquidate at the End Date (end on EndDate, and at 12pm that day). 
        self.Schedule.On(self.DateRules.On(self.EndDate.year, self.EndDate.month, self.EndDate.day),  
                         self.TimeRules.At(12, 0),
                         lambda: self.Liquidate())
    

        # Bitfinex accepts both Cash and Margin type account.
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/btcusd_quote.zip/btcusd.csv
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/ethusd_quote.zip/ethusd.csv
        # self.AddUniverse(CryptoCoarseFundamentalUniverse(Market.Bitfinex, self.UniverseSettings, self.UniverseSelectionFilter))
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Cash)
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Margin)

        if Config.CRYPTO:
            self.ind_symbol = self.AddCrypto(Config.IND_ASSET, Resolution.Daily, Market.Bitfinex).Symbol
        else:
            self.ind_symbol = self.AddEquity(Config.IND_ASSET, Resolution.Daily).Symbol

        self.loglimit = 35

    def OnData(self, data: Slice):

        # Check Logs (only put logs here to limit the # of logs you use per test)
        if self.loglimit != 0:
            # self.Log("Hello there!")
            pass

        if not self.Portfolio.Invested:
            self.SetHoldings(self.ind_symbol, 1)
         