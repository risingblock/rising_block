# Absolute Momentum
from catalyst import run_algorithm
from catalyst.api import record
import pandas as pd
import matplotlib.pyplot as plt
from catalyst.exchange.utils.stats_utils import extract_transactions, get_pretty_stats
import numpy as np
from momentum.DualMomentumAsset import DualMomentumAsset


def initialize(context):
    context.i = 0
    context.look_back_window = 14400
    context.set_long_only()
    context.btc = DualMomentumAsset('btc', context, 'btc_usdt')
    context.eth = DualMomentumAsset('eth', context, 'eth_usdt')
    context.xrp = DualMomentumAsset('xrp', context, 'xrp_usdt')
    context.ltc = DualMomentumAsset('ltc', context, 'ltc_usdt')
    context.bch = DualMomentumAsset('bch', context, 'bch_usdt')
    context.eos = DualMomentumAsset('eos', context, 'eos_usdt')
    context.neo = DualMomentumAsset('neo', context, 'neo_usdt')
    context.qtum = DualMomentumAsset('qtum', context, 'qtum_usdt')

    context.assets = [context.btc, context.eth, context.ltc, context.xrp, context.bch, context.eos, context.neo, context.qtum]


def handle_data(context, data):
    # Skip bars until we can calculate momentum
    context.i += 1
    if context.i < context.look_back_window:
        return
    btc_price = data.current(context.btc.asset_usdt, 'price')

    if context.i % context.look_back_window == 0:
        highest_momentum_value = 0
        highest_momentum_asset = None
        for asset in context.assets:
            asset_momentum = asset.get_momentum(data)
            if asset_momentum > highest_momentum_value:
                highest_momentum_asset = asset
                highest_momentum_value = asset_momentum

        if highest_momentum_value > 0:
            print("buying {}, with momentum of {} at {}".format(highest_momentum_asset.name, highest_momentum_value, data.current_dt))
            for asset in context.assets:
                if asset.name != highest_momentum_asset.name:
                    asset.sell_all()
            highest_momentum_asset.buy_all()

        else:
            print("Bear market sell all at {}".format(data.current_dt))
            for asset in context.assets:
                asset.sell_all()

    record(btc_price=btc_price, cash=context.portfolio.cash)


def analyze(context, perf):
    stats = get_pretty_stats(perf)
    print('the algo stats:\n{}'.format(stats))
    # Get the base_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    base_currency = exchange.quote_currency.upper()

    # First chart: Plot portfolio value using base_currency
    ax1 = plt.subplot(411)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(base_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    ax2 = plt.subplot(412, sharex=ax1)
    perf.loc[:, ['btc_price']].plot(
        ax=ax2,
        label='PriceB', color='orange')
    ax2.legend_.remove()
    ax2.set_ylabel('BTC USDT')
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
    plt.show()


if __name__ == '__main__':
    run_algorithm(
        analyze=analyze,
        capital_base=1000,
        initialize=initialize,
        handle_data=handle_data,
        exchange_name='binance',
        algo_namespace='dual_momentum_asdfsadf',
        quote_currency='usd',
        live=True,
        simulate_orders=True,
        # start=pd.to_datetime('2016-01-01', utc=True),
        # end=pd.to_datetime('2018-03-01', utc=True),
    )