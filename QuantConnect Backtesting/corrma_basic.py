# region imports
from AlgorithmImports import *
from QuantConnect.DataSource import *
from QuantConnect.Data.UniverseSelection import *
# endregion
import datetime

from indicator import CustomCorrelationMovingAverage

class CorrmaAlgo(QCAlgorithm):

    def Initialize(self):
        '''
        QC_OPTIMIZING = False when running individual tests. True when using QC Optimization testing.

        CRYPTO = True if using crypto assets, False otherwise (for stocks/ETFs, etc.)
        IND_ASSET = Starting asset. Swap to DEP_ASSET when CORRMA < THRESHOLD.
        DEP_ASSET = Swapped asset.

        WINDOW = # of days to set as the correlation moving average
        THRESHOLD = correlation threshold to check for on the moving average and trigger a trade.
        CASH = starting cash value (USD)
        START_DATE
        END_DATE 
        self.loglimit = # of logs to display before stopping to save $.

        Current testing indicates that if the IND_ASSET is the "more volatile" asset, and the DEP_ASSET is the "larger cap/less volatile" asset, this generates better returns (crypto).
        '''
        # QuantConnect Optimization
        QC_OPTIMIZING = False

        # Set Assets
        CRYPTO = True
        IND_ASSET = "ETHUSD"        # "AMZN"
        DEP_ASSET = "BTCUSD"        # "XLY"

        # Set Values
        WINDOW = 90
        THRESHOLD = 0.3
        CASH = 100000
        START_DATE = datetime.date(2017, 1, 1)      # Year, Month, Day
        END_DATE = datetime.date(2022, 11, 22)
        # END_DATE = datetime.now() - datetime.timedelta(7)    # 7 days before today

        # Local log variable to limit the number of messages (QuantConnect has a limit)
        self.loglimit = 0


        # Initialization
        if not QC_OPTIMIZING:
            self.window = WINDOW
            self.corrma_ratio = THRESHOLD
        else:
            self.window = int(self.GetParameter("window"))
            self.corrma_ratio = float(self.GetParameter("threshold"))

        self.SetCash(CASH)  
        self.SetStartDate(START_DATE)
        self.SetEndDate(END_DATE)

        # Set Account to Liquidate at the End Date (end on EndDate, and at 12pm that day). 
        self.Schedule.On(self.DateRules.On(self.EndDate.year, self.EndDate.month, self.EndDate.day),  
                         self.TimeRules.At(12, 0),
                         lambda: self.Liquidate())

        # Set the warm up period
        self.SetWarmup(datetime.timedelta(self.window))

        # Bitfinex accepts both Cash and Margin type account.
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/btcusd_quote.zip/btcusd.csv
        # https://www.quantconnect.com/data/file/crypto/bitfinex/daily/ethusd_quote.zip/ethusd.csv
        # self.AddUniverse(CryptoCoarseFundamentalUniverse(Market.Bitfinex, self.UniverseSettings, self.UniverseSelectionFilter))

        # For Crypto Only
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Cash)
        # self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Margin)

        # Set the assets
        if CRYPTO:
            self.ind_symbol = self.AddCrypto(IND_ASSET, Resolution.Daily, Market.Bitfinex).Symbol
            self.dep_symbol = self.AddCrypto(DEP_ASSET, Resolution.Daily, Market.Bitfinex).Symbol
        else:
            self.ind_symbol = self.AddEquity(IND_ASSET, Resolution.Daily).Symbol
            self.dep_symbol = self.AddEquity(DEP_ASSET, Resolution.Daily).Symbol
            
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
        if not self.IsWarmingUp and self.corrma.IsReady and self.EndDate - self.Time > datetime.timedelta(1):
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
