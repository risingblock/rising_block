from catalyst.api import order_target_percent, symbol


class DualMomentumAsset:
    def __init__(self, name, context, asset_usdt):
        self.name = name
        self.context = context
        self.asset_usdt = symbol(asset_usdt)

    def sell_all(self):
        if self.context.portfolio.positions[self.asset_usdt].amount > 0:
            print("selling {}, amount {}, name {}, for usdt".format(self.name, self.context.portfolio.positions[self.asset_usdt].amount, self.asset_usdt.asset_name))
            order_target_percent(self.asset_usdt, 0)

    def buy_all(self):
        if self.context.portfolio.positions[self.asset_usdt].amount == 0:
            print("buying {} w/ usdt".format(self.name))
            order_target_percent(self.asset_usdt, 1)

    def get_momentum(self, data):
        history = data.history(self.asset_usdt, 'price', bar_count=10,
                               frequency='1D')
        return history.pct_change(self.context.look_back_window - 1)[-1] * 100
