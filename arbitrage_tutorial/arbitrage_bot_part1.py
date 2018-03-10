from catalyst.api import symbol, order
from catalyst.utils.run_algo import run_algorithm
import pandas as pd


def initialze(context):
    context.bittrex = context.exchanges['bitfinex']
    context.poloniex = context.exchanges['poloniex']

    context.bittrex_trading_pair = symbol('eth_btc', context.bittrex.name)
    context.poloniex_trading_pair = symbol('eth_btc', context.poloniex.name)


def handle_data(context, data):
    poloneix_price = data.current(context.poloniex_trading_pair, 'price')
    bittrex_price = data.current(context.bittrex_trading_pair, 'price')

    print('Date: {}'.format(data.current_dt))
    print('Poloniex: {}'.format(poloneix_price))
    print('Bittrex: {}'.format(bittrex_price))

    if (poloneix_price > bittrex_price):
        # Buy bittrex, sell poloneix
        print('Buy bittrex, selling poloneix')
        order(asset=context.bittrex_trading_pair,
              amount=1,
              limit_price=bittrex_price)
        order(asset=context.poloniex_trading_pair,
              amount=-1,
              limit_price=poloneix_price)

    elif (bittrex_price > poloneix_price):
        print('Buy poloneix, selling bittrex')
        order(asset=context.poloniex_trading_pair,
              amount=1,
              limit_price=poloneix_price)
        order(asset=context.bittrex_trading_pair,
              amount=-1,
              limit_price=bittrex_price)


def analyze(context):
    # TODO: Next tutorial
    pass


perf = run_algorithm(capital_base=100,
              initialize=initialze,
              handle_data=handle_data,
              analyze=analyze,
              live=False,
              base_currency='btc',
              exchange_name='bitfinex, poloniex',
              data_frequency='minute',
              start=pd.to_datetime('2017-12-12', utc=True),
              end=pd.to_datetime('2017-12-13', utc=True))