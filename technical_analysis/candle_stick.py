# Absolute Momentum
from catalyst import run_algorithm
from catalyst.api import order_target_percent, record, symbol
import pandas as pd
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go

def plt_show():
    try:
        plt.show()
    except UnicodeDecodeError:
        plt_show()


def initialize(context):
    context.asset = symbol('btc_usdt')
    context.i = 0
    context.holding = False
    context.interval = 240


def handle_data(context, data):
    context.i += 1
    high_history = data.history(context.asset, 'high', bar_count=3, frequency="1D")
    low_history = data.history(context.asset, 'low', bar_count=3, frequency="1D")

    open = data.current(context.asset, 'open')
    high = data.current(context.asset, 'high')
    low = data.current(context.asset, 'low')
    close = data.current(context.asset, 'close')
    volume = data.current(context.asset, 'volume')
    price = data.current(context.asset, 'price')

    signal = inside_bar_signal(high_history, low_history)
    if signal == 1:
        # Bull break
        print("Bull break")
        order_target_percent(context.asset, 1)
    elif signal == -1:
        # Bear break
        print("Bear break")
        order_target_percent(context.asset, 0)
    record(open=open,
           high=high,
           low=low,
           close=close,
           volume=volume,
           price=price,
           signal=signal)


def analyze(context, perf):
    trace0 = go.Ohlc(x=perf.index.to_series(),
                     open=perf.open,
                     high=perf.high,
                     low=perf.low,
                     close=perf.close,
                     showlegend=False)

    pos_values = perf.signal[perf.signal > 0]
    pos_high_values = perf.high[perf.high.index.isin(pos_values.index)]
    neg_values = perf.signal[perf.signal < 0]
    neg_low_values = perf.high[perf.high.index.isin(neg_values.index)]

    trace1 = go.Scatter(
        x=pos_values.index.to_series(),
        y=pos_high_values,
        mode='markers',
        name='Bull Break'
    )

    trace2 = go.Scatter(
        x=neg_values.index.to_series(),
        y=neg_low_values,
        mode='markers',
        name='Bear Break'
    )

    data = [trace0, trace1, trace2]
    py.plot(data, filename='simple_ohlc2')


def inside_bar_signal(highs, lows):
    if highs[0] > highs[1] and lows[0] < lows[1]:
        if highs[2] > highs[1] and lows[2] < lows[1]:
            # Market range is increasing
            return 0
        if highs[2] > highs[1]:
            # Bull signal
            return 1
        elif lows[2] < lows[1]:
            # Bear signal
            return -1
        # No signal, still inside
    return 0


if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        exchange_name='poloniex',
        algo_namespace='momentum',
        quote_currency='usd',
        live=False,
        analyze=analyze,
        start=pd.to_datetime('2017-02-14', utc=True),
        end=pd.to_datetime('2017-06-30', utc=True),
    )
