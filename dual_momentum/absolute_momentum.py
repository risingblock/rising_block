# Absolute Momentum
from catalyst import run_algorithm
from catalyst.api import order_target_percent, record, symbol
import pandas as pd
import matplotlib.pyplot as plt
from catalyst.exchange.utils.stats_utils import extract_transactions, get_pretty_stats
import numpy as np


def initialize(context):
    context.asset = symbol('btc_usdt')
    context.i = 0
    context.holding = False


def handle_data(context, data):
    look_back_window = 20

    # Skip bars until we can calculate absolute momentum
    context.i += 1
    if context.i < look_back_window:
        return

    btc_history = data.history(context.asset, 'price', bar_count=look_back_window, frequency='1D')

    percentage_change = btc_history.pct_change(look_back_window - 1)[-1] * 100
    price = data.current(context.asset, 'price')

    # Trading logic

    # Buy if the percentage change > 0
    if percentage_change > 0:
        if not context.holding:
            order_target_percent(context.asset, 1)
            context.holding = True
    # Sell otherwise
    else:
        if context.holding:
            order_target_percent(context.asset, 0)
            context.holding = False

    record(price=price,
           cash=context.portfolio.cash,
           percent_change=percentage_change)


def analyze(context, perf):
    stats = get_pretty_stats(perf)
    print('the algo stats:\n{}'.format(stats))
    # Get the base_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    base_currency = exchange.base_currency.upper()

    # First chart: Plot portfolio value using base_currency
    ax1 = plt.subplot(411)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(base_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    ax2 = plt.subplot(412, sharex=ax1)
    perf.loc[:, ['price']].plot(
        ax=ax2,
        label='Price')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({base})'.format(
        asset=context.asset.symbol,
        base=base_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(0, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        ax2.scatter(
            transaction_df.index.to_pydatetime(),
            perf.loc[transaction_df.index, 'price'],
            marker='x',
            s=150,
            c='black',
            label=''
        )

    # Plot our cash
    ax3 = plt.subplot(413, sharex=ax1)
    perf.cash.plot(ax=ax3)
    ax3.set_ylabel('Cash\n({})'.format(base_currency))
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(0, end, end / 5))

    # Plot % change in look back period
    percent_change_data = perf.loc[:, ['percent_change']]
    pos_percent_change = percent_change_data.copy()
    neg_percent_change = percent_change_data.copy()

    pos_percent_change[pos_percent_change <= 0] = np.nan
    neg_percent_change[neg_percent_change > 0] = np.nan

    ax4 = plt.subplot(414, sharex=ax1)
    pos_percent_change.loc[:, ['percent_change']].plot(
        ax=ax4,
        color='g')

    neg_percent_change.loc[:, ['percent_change']].plot(
        ax=ax4,
        color='r')

    ax4.set_ylabel('% change 28 d\n({})'.format(base_currency))
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(start, end, end / 5))
    ax4.legend_.remove()

    plt.show()


if __name__ == '__main__':
    run_algorithm(
        analyze=analyze,
        capital_base=10000,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        exchange_name='bittrex',
        algo_namespace='dual_momentum',
        base_currency='usd',
        live=False,
        start=pd.to_datetime('2017-09-20', utc=True),
        end=pd.to_datetime('2018-03-23', utc=True),
    )