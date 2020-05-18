from pyalgotrade.barfeed import csvfeed
from pyalgotrade.broker import backtesting
from pyalgotrade import plotter
from ma_cross_strategy import MACrossoverStrategy

def run_strategy(fastSma, slowSma, tp, stop):
    # Load the bar feed from the CSV file
    feed = csvfeed.GenericBarFeed(frequency=60*5)
    feed.setDateTimeFormat("%Y-%m-%dT%H:%M:%S.%fZ")
    feed.addBarsFromCSV("btc", "btc-5m-apr.csv")
    
    # Create our broker defining the comission(0,01%) and the initial balance($15000)
    commission = backtesting.TradePercentage(0.0001)
    broker = backtesting.Broker(15000, feed, commission)

    # Evaluate the strategy with the feed
    myStrategy = MACrossoverStrategy(feed, "btc", broker, fastSma, slowSma, tp, stop)

    # Attach the plotter to the strategy
    plt = plotter.StrategyPlotter(myStrategy)

    # Include the MA in the instrument's subplot to get it displayed along with the closing prices
    plt.getOrCreateSubplot("MA").addDataSeries("50 MA", myStrategy.getFastSMA())
    plt.getOrCreateSubplot("MA").addDataSeries("200 MA", myStrategy.getSlowSMA())

    # Run the strategy and show the final portfolio value
    myStrategy.run()
    myStrategy.info(f'Final portfolio value: ${myStrategy.getResult()}')

    # Plot the strategy
    plt.plot()

run_strategy(50, 200, 0.018, 0.003)