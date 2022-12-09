# region imports
from AlgorithmImports import *
from QuantConnect.DataSource import *
from QuantConnect.Data.UniverseSelection import *
# endregion
from datetime import datetime, timedelta
from collections import deque

class CorrmaAlgo(QCAlgorithm):

    def Initialize(self):
        '''
        window = # of days to set as the correlation moving average
        corrma = correlation threshold to check for on the moving average and trigger a trade. 
        '''
        self.window = 30
        self.corrma_ratio = 0.0

        self.SetCash(100000)  
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2022, 11, 22)
        # self.SetEndDate(datetime.now() - timedelta(7))

        # Set Account to Liquidate at the End Date (end on EndDate, and at 12pm that day). 
        self.Schedule.On(self.DateRules.On(self.EndDate.year, self.EndDate.month, self.EndDate.day),  
                         self.TimeRules.At(12, 0),
                         lambda: self.Liquidate())

        # Set the warm up period
        # self.SetWarmup(timedelta(self.window))

        # Bitfinex accepts both Cash and Margin type account.
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/btcusd_quote.zip/btcusd.csv
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/ethusd_quote.zip/ethusd.csv
        # self.AddUniverse(CryptoCoarseFundamentalUniverse(Market.Bitfinex, self.UniverseSettings, self.UniverseSelectionFilter))

        # For Crypto Only
        self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Cash)
        self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Margin)

        # Set the assets
        self.ind_symbol = self.AddCrypto("BTCUSD", Resolution.Daily, Market.Bitfinex).Symbol
        self.dep_symbol = self.AddCrypto("ETHUSD", Resolution.Daily, Market.Bitfinex).Symbol
            
        # Custom CORMRMA Indicator
        self.corrma = CustomCorrelationMovingAverage("CORRMA", self.window)
        self.corrma_triggered = False

        self.loglimit = 35


    def OnData(self, data: Slice):

        # Check Logs (only put logs here to limit the # of logs you use per test)
        if self.loglimit != 0:
            # self.Log(self.corrma.__repr__())
            # self.Log(self.EndDate - self.Time)
            self.loglimit -= 1

        # NOTE - Crypto trading in Quant Connect needs different methods compared to traditional assets and securities
        # https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/crypto-trades
        # However, I'm just not going to worry about this for now and just trade with the asset pairs! :D

        # Initially purchase the independent symbol
        if not self.Portfolio.Invested:
            self.SetHoldings(self.ind_symbol, 1)
            

        # Update the indicator manually
        if data.ContainsKey(self.ind_symbol): 
            dp = data[self.ind_symbol]
            self.corrma.Update(input=dp, ind_bar=True)

        if data.ContainsKey(self.dep_symbol):
            dp = data[self.dep_symbol] 
            self.corrma.Update(input=dp, ind_bar=False)

        
        # Use the indicator to make trading decisions (only trade if indicator is ready AND it's not the last day of the algorithm - edge case for scheduling the Liquidate())
        if self.corrma.IsReady and self.EndDate - self.Time > timedelta(1):
            value = self.corrma.Value

            if value <= self.corrma_ratio and not self.corrma_triggered:
                self.corrma_triggered = True
                # Swap to the other asset
                self.Liquidate(self.ind_symbol)
                self.SetHoldings(self.dep_symbol, 1)

            if value > self.corrma_ratio and self.corrma_triggered:
                self.corrma_triggered = False
                # Swap back to the original assset
                self.Liquidate(self.dep_symbol)
                self.SetHoldings(self.ind_symbol, 1)


# Custom Corrma Indicator
class CustomCorrelationMovingAverage(PythonIndicator):
    import pandas as pd

    def __init__(self, name, period):
        self.Name = name 
        # self.WarmUpPeriod = period * 2             # How long to initialize
        # This WarmUpPeriod pumps in data from BEFORE the start of the algorithm... Am I worried about that?
        self.Time = datetime.min                # Initial value
        self.Value = 0.0                        # Initial value
        self.ind_queue = deque(maxlen=period)   # I think this sets the max # of data rows the indicator can store
        self.dep_queue = deque(maxlen=period)

        self.myupdate = False

    def __repr__(self):
        return f"{self.Name} -> IsReady: {self.IsReady}. Time: {self.Time}. Value: {self.Value}. Ind Queue (Len vs. Max): ({len(self.ind_queue)}, {self.ind_queue.maxlen}). Dep Queue (Len vs. Max): ({len(self.dep_queue)}, {self.dep_queue.maxlen})"

    @property
    def IsReady(self) -> bool:
        return len(self.ind_queue) == self.ind_queue.maxlen and len(self.dep_queue) == self.dep_queue.maxlen

    def Update(self, input: BaseData, ind_bar: bool) -> bool:
        if ind_bar:
            self.ind_queue.append(input.Value)
        else:
            self.dep_queue.append(input.Value)

        self.Time = input.Time 

        if self.IsReady:
            self.Value = pd.DataFrame({'col1': self.ind_queue, 'col2': self.dep_queue}).corr().iloc[0].iloc[1]

        # Supposed to "Show when indicator IsReady", but I think it's broken.
        return len(self.ind_queue) == self.ind_queue.maxlen and len(self.dep_queue) == self.dep_queue.maxlen
