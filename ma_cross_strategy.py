from pyalgotrade import strategy
from pyalgotrade.technical import ma

class MACrossoverStrategy(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument, broker, fastMA, slowMA, takeProfitMultiplier, stopMultiplier):
        super(MACrossoverStrategy, self).__init__(feed, broker)
        self.__instrument = instrument
        self.__fast_ma = ma.SMA(feed[instrument].getPriceDataSeries(), fastMA)
        self.__slow_ma = ma.SMA(feed[instrument].getPriceDataSeries(), slowMA)
        self.__takeProfitMultiplier = takeProfitMultiplier
        self.__stopMultiplier = stopMultiplier

        self.__takeProfitPrice = None
        self.__stopPrice = None
        self.__position = None
        self.__lastTrend = None

    def getFastSMA(self):
        return self.__fast_ma

    def getSlowSMA(self):
        return self.__slow_ma

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate Moving Averages
        if self.__fast_ma[-1] is None or self.__slow_ma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If we don't have an open position, we check if there is an trend reversal
        if self.__position is None:
            if self.__fast_ma[-1] > self.__slow_ma[-1] and self.__lastTrend != 'BULL':
                # If the trend is bullish, we buy 1 bitcoin and calculate the
                # take profit and stop loss prices
                self.__position = self.enterLong(self.__instrument, 1, True)
                self.__takeProfitPrice = bar.getPrice() * (1 + self.__takeProfitMultiplier)
                self.__stopPrice = bar.getPrice() * (1 - self.__stopMultiplier)
                self.__lastTrend = 'BULL'
                
            elif self.__fast_ma[-1] < self.__slow_ma[-1] and self.__lastTrend != 'BEAR':
                # If the trend is bearish, we sell 1 bitcoin and calculate the
                # take profit and stop loss prices
                self.__position = self.enterShort(self.__instrument, 1, True)
                self.__takeProfitPrice = bar.getPrice() * (1 - self.__takeProfitMultiplier)
                self.__stopPrice = bar.getPrice() * (1 + self.__stopMultiplier)
                self.__lastTrend = 'BEAR'
        else:
            # If we have an open position, we check if the asset price got to our take profit
            # or stop loss price
            if self.__position.getShares() > 0:
                if bar.getPrice() > self.__takeProfitPrice or bar.getPrice() < self.__stopPrice:
                    self.__position.exitMarket()
                    self.__position = None
            elif self.__position.getShares() < 0:
                if bar.getPrice() < self.__takeProfitPrice or bar.getPrice() > self.__stopPrice:
                    self.__position.exitMarket()
                    self.__position = None