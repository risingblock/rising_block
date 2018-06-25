# Absolute Momentum
import talib
from catalyst import run_algorithm
from catalyst.api import order_target_percent, record, symbol
import pandas as pd
from util.data import fill


def initialize(context):
    context.asset = symbol('btc_usdt')
    context.i = 0
    context.holding = False
    context.lookback = 1


def handle_data(context, data):
    one_day_in_minutes = 1440  # 60 * 24 assumes data_frequency='minute'
    minutes = 30
    lookback_days = 1  # 7 days
    lookback = int(one_day_in_minutes / minutes * lookback_days)

    # Skip bars until we can calculate absolute momentum
    context.i += 1
    if context.i < lookback:
        return

    # Get 30 minute interval OHLCV data. This is the standard data
    # required for candlestick or indicators/signals. Return Pandas
    # DataFrames. 30T means 30-minute re-sampling of one minute data.
    # Adjust it to your desired time interval as needed.
    open = fill(data.history(context.asset,
                               'open',
                               bar_count=lookback,
                               frequency='240T')).values
    high = fill(data.history(context.asset,
                             'high',
                             bar_count=lookback,
                             frequency='240T')).values
    low = fill(data.history(context.asset,
                            'low',
                            bar_count=lookback,
                            frequency='240T')).values
    close = fill(data.history(context.asset,
                              'price',
                              bar_count=lookback,
                              frequency='240T')).values
    volume = fill(data.history(context.asset,
                               'volume',
                               bar_count=lookback,
                               frequency='240T')).values


if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        exchange_name='poloniex',
        algo_namespace='momentum',
        quote_currency='usd',
        live=False,
        start=pd.to_datetime('2017-09-20', utc=True),
        end=pd.to_datetime('2018-03-23', utc=True),
    )