from datetime import datetime

class Config:
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

        Current testing indicates that if the IND_ASSET is the "more volatile" asset, and the DEP_ASSET is the "larger cap/less volatile" asset, this generates better returns (crypto).
        '''
        # QuantConnect Optimization
        QC_OPTIMIZING = False

        # Set Assets
        CRYPTO = True
        IND_ASSET = "ETHUSD"        # "AMZN" -> Also used in benchmark_v2.py
        DEP_ASSET = "BTCUSD"        # "XLY"

        # Set Values
        WINDOW = 90
        THRESHOLD = 0.3
        CASH = 100000
        START_DATE = datetime.date(2017, 1, 1)      # Year, Month, Day
        END_DATE = datetime.date(2022, 11, 22)
        END_DATE = datetime.datetime.now()
        # END_DATE = datetime.now() - datetime.timedelta(7)    # 7 days before today
