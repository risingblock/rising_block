# Absolute Momentum
from catalyst import run_algorithm
from catalyst.api import order_target_percent, order_target, record, symbol
import pandas as pd
import matplotlib.pyplot as plt
from catalyst.exchange.utils.stats_utils import extract_transactions, get_pretty_stats
import numpy as np


def initialize(context):
    context.i = 0
    context.eth_btc = symbol('eth_btc')
    context.btc_usdt = symbol('btc_usdt')
    context.eth_usdt = symbol('eth_usdt')

    #NEO
    context.neo_usdt = symbol('neo_usdt')
    context.neo_btc = symbol('neo_btc')
    context.neo_eth = symbol('neo_eth')

    context.look_back_window = 2
    context.frequency = '1D' if context.data_frequency == 'daily' else '1M'
    context.set_long_only()


def handle_data(context, data):
    # Skip bars until we can calculate momentum
    context.i += 1
    if context.i < context.look_back_window:
        return
    btc_price = data.current(context.btc_usdt, 'price')
    eth_price = data.current(context.eth_usdt, 'price')

    # Calculate momentum
    btc_history = data.history(context.btc_usdt, 'price', bar_count=context.look_back_window,
                               frequency=context.frequency)
    eth_history = data.history(context.eth_usdt, 'price', bar_count=context.look_back_window,
                               frequency=context.frequency)
    neo_history = data.history(context.neo_usdt, 'price', bar_count=context.look_back_window,
                               frequency=context.frequency)

    btc_momentum = btc_history.pct_change(context.look_back_window - 1)[-1] * 100
    eth_momentum = eth_history.pct_change(context.look_back_window - 1)[-1] * 100
    neo_momentum = neo_history.pct_change(context.look_back_window - 1)[-1] * 100

    btc_usdt_amount = context.portfolio.positions[context.btc_usdt].amount
    eth_usdt_amount = context.portfolio.positions[context.eth_usdt].amount
    eth_btc_amount = context.portfolio.positions[context.eth_btc].amount
    neo_usdt_amount = context.portfolio.positions[context.neo_usdt].amount
    neo_btc_amount = context.portfolio.positions[context.neo_btc].amount
    neo_eth_amount = context.portfolio.positions[context.neo_eth].amount

    # trade only once every look back window
    if context.i % context.look_back_window == 0:
        if btc_momentum < 0 and eth_momentum < 0 and neo_momentum < 0:
            # Hold USDT, bear market
            print("Bear market sell all at {}".format(data.current_dt))
            if btc_usdt_amount > 0:
                print("sell all btc for usdt")
                order_target_percent(context.btc_usdt, 0)
            elif eth_usdt_amount > 0:
                print("sell all eth for usdt")
                order_target_percent(context.eth_usdt, 0)
            elif eth_btc_amount > 0:
                order_target_percent(context.eth_btc, 0)
            elif neo_usdt_amount > 0:
                print("selling all neo_usdt")
                order_target_percent(context.neo_usdt, 0)
            elif neo_btc_amount > 0:
                print("selling all neo_btc")
                order_target_percent(context.neo_btc, 0)
            elif neo_eth_amount > 0:
                print("selling all neo_eth")
                order_target_percent(context.neo_eth, 0)

        # Trading logic
        elif btc_momentum > eth_momentum: #and btc_momentum > neo_momentum:
            print("BTC mom: {} > ETH mom: {}, buying btc at {}".format(btc_momentum, eth_momentum, data.current_dt))
            if eth_btc_amount > 0:
                print("Buying btc with eth")
                order_target_percent(context.eth_btc, 0)
            if btc_usdt_amount == 0:
                print("Buying btc with usdt")
                order_target_percent(context.btc_usdt, 1)
            if neo_btc_amount == 0:
                order_target_percent(context.neo_btc, 0)
                print("selling neo buying btc {}".format(data.current_dt))
        elif eth_momentum > btc_momentum: #and eth_momentum > neo_momentum:
            print("BTC mom: {} < ETH mom: {}, buying eth at {}".format(btc_momentum, eth_momentum, data.current_dt))
            if eth_btc_amount == 0:
                print("Buying eth with btc")

                order_target_percent(context.eth_btc, 1)
            if eth_usdt_amount == 0:
                print("Buying eth with usdt")

                order_target_percent(context.eth_usdt, 1)
            if neo_eth_amount > 0:
                print("selling NEO, buying eth at {}".format(data.current_dt))
                order_target_percent(context.neo_eth, 0)
        elif neo_momentum > btc_momentum and neo_momentum > eth_momentum:
            if neo_eth_amount == 0:
                print("buying neo with eth {}".format(data.current_dt))
                order_target_percent(context.neo_eth, 1)
            if neo_usdt_amount == 0:
                order_target_percent(context.neo_usdt, 1)
                print("Buying neo with USD at {}".format(data.current_dt))
            if neo_eth_amount > 0:
                print("Buying NEO, with btc at {}".format(data.current_dt))
                order_target_percent(context.neo_btc, 1)

    record(eth_price=eth_price,
           btc_price=btc_price,
           cash=context.portfolio.cash,
           percent_change_btc=btc_momentum,
           percent_change_eth=eth_momentum)


def analyze(context, perf):
    stats = get_pretty_stats(perf)
    print('the algo stats:\n{}'.format(stats))
    # Get the base_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    # First chart: Plot portfolio value using base_currency
    ax1 = plt.subplot(411)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    ax2 = plt.subplot(412, sharex=ax1)
    perf.loc[:, ['btc_price']].plot(
        ax=ax2,
        label='PriceB', color='orange')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({base})'.format(
        asset=context.btc_usdt.symbol,
        base=quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(0, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        ax2.scatter(
            transaction_df.index.to_pydatetime(),
            perf.loc[transaction_df.index, 'btc_price'],
            marker='x',
            s=150,
            c='black',
            label=''
        )

    # Plot eth % change in look back period
    percent_change_data = perf.loc[:, ['percent_change_eth']]
    pos_percent_change = percent_change_data.copy()
    neg_percent_change = percent_change_data.copy()

    pos_percent_change[pos_percent_change <= 0] = np.nan
    neg_percent_change[neg_percent_change > 0] = np.nan

    ax3 = plt.subplot(413, sharex=ax1)
    pos_percent_change.loc[:, ['percent_change_eth']].plot(
        ax=ax3,
        color='g')

    neg_percent_change.loc[:, ['percent_change_eth']].plot(
        ax=ax3,
        color='r')

    ax3.set_ylabel('% change eth')
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(start, end, end / 5))
    ax3.legend_.remove()

    # Plot BTC % change in look back period
    percent_change_data = perf.loc[:, ['percent_change_btc']]
    pos_percent_change = percent_change_data.copy()
    neg_percent_change = percent_change_data.copy()

    pos_percent_change[pos_percent_change <= 0] = np.nan
    neg_percent_change[neg_percent_change > 0] = np.nan

    ax4 = plt.subplot(414, sharex=ax1)
    pos_percent_change.loc[:, ['percent_change_btc']].plot(
        ax=ax4,
        color='g')

    neg_percent_change.loc[:, ['percent_change_btc']].plot(
        ax=ax4,
        color='r')

    ax4.set_ylabel('% change btc')
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(start, end, end / 5))
    ax4.legend_.remove()

    plt.show()


if __name__ == '__main__':
    run_algorithm(
        analyze=analyze,
        capital_base=1000,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        exchange_name='bitfinex',
        algo_namespace='dual_momentum_2',
        quote_currency='usd',
        live=False,
        start=pd.to_datetime('2017-09-08', utc=True),
        end=pd.to_datetime('2018-01-20', utc=True),
    )