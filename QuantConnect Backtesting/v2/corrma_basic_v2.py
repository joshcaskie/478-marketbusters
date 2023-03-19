# region imports
from AlgorithmImports import *
from QuantConnect.DataSource import *
from QuantConnect.Data.UniverseSelection import *
# endregion
from datetime import timedelta

from indicator import CustomCorrelationMovingAverage
from config import Config

class CorrmaAlgoV2(QCAlgorithm):

    def Initialize(self):
        # Local log variable to limit the number of messages (QuantConnect has a limit)
        self.loglimit = 0

        # Initialization
        if not Config.QC_OPTIMIZING:
            self.window = Config.WINDOW
            self.corrma_ratio = Config.THRESHOLD
        else:
            self.window = int(self.GetParameter("window"))
            self.corrma_ratio = float(self.GetParameter("threshold"))

        self.SetCash(Config.CASH)  
        self.SetStartDate(Config.START_DATE)
        self.SetEndDate(Config.END_DATE)

        # Set Account to Liquidate at the End Date (end on EndDate, and at 12pm that day). 
        self.Schedule.On(self.DateRules.On(self.EndDate.year, self.EndDate.month, self.EndDate.day),  
                         self.TimeRules.At(12, 0),
                         lambda: self.Liquidate())

        # Set the warm up period
        self.SetWarmup(timedelta(self.window))

        # Bitfinex accepts both Cash and Margin type account.
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/btcusd_quote.zip/btcusd.csv
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/ethusd_quote.zip/ethusd.csv
        # self.AddUniverse(CryptoCoarseFundamentalUniverse(Market.Bitfinex, self.UniverseSettings, self.UniverseSelectionFilter))

        # For Crypto Only
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Cash)
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Margin)

        # Set the assets
        if Config.CRYPTO:
            self.ind_symbol = self.AddCrypto(Config.IND_ASSET, Resolution.Daily, Market.Bitfinex).Symbol
            self.dep_symbol = self.AddCrypto(Config.DEP_ASSET, Resolution.Daily, Market.Bitfinex).Symbol
        else:
            self.ind_symbol = self.AddEquity(Config.IND_ASSET, Resolution.Daily).Symbol
            self.dep_symbol = self.AddEquity(Config.DEP_ASSET, Resolution.Daily).Symbol
            
        # Custom CORMRMA Indicator
        self.corrma = CustomCorrelationMovingAverage("CORRMA", self.window)
        self.corrma_triggered = False


    def OnData(self, data: Slice):

        # Check Logs (only put logs here to limit the # of logs you use per test)
        if self.loglimit != 0:
            self.Log(self.corrma.__repr__())
            # self.Log(self.EndDate - self.Time)
            self.loglimit -= 1

        # NOTE - Crypto trading in Quant Connect needs different methods compared to traditional assets and securities
        # https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/crypto-trades
        # However, I'm just not going to worry about this for now and just trade with the asset pairs! :D

        # Update the indicator manually
        if data.ContainsKey(self.ind_symbol): 
            dp = data[self.ind_symbol]
            self.corrma.Update(input=dp, ind_bar=True)

        if data.ContainsKey(self.dep_symbol):
            dp = data[self.dep_symbol] 
            self.corrma.Update(input=dp, ind_bar=False)

        
        # Use the indicator to make trading decisions (only trade if indicator is ready AND it's not the last day of the algorithm - edge case for scheduling the Liquidate())
        if not self.IsWarmingUp and self.corrma.IsReady and self.EndDate - self.Time > timedelta(1):
            # Initially purchase the independent symbol
            if not self.Portfolio.Invested:
                self.SetHoldings(self.ind_symbol, 1)

            value = self.corrma.Value

            if value <= self.corrma_ratio and not self.corrma_triggered:
                self.corrma_triggered = True
                # Swap to the other asset
                self.Liquidate(self.ind_symbol)
                self.SetHoldings(self.dep_symbol, 1)

            if value > self.corrma_ratio and self.corrma_triggered:
                self.corrma_triggered = False
                # Swap back to the original asset
                self.Liquidate(self.dep_symbol)
                self.SetHoldings(self.ind_symbol, 1)
