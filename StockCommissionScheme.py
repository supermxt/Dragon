import backtrader as bt


class StockCommissionScheme(bt.CommInfoBase):
    params = (
        ('stampduty', 0.005),  # 印花税率
        ('commission', 0.005),  # 佣金率
        ('stocklike', True),  # 股票类资产，不考虑保证金
        ('commtype', bt.CommInfoBase.COMM_PERC),  # 按百分比
        ('minCommission', 5),  # 最小佣金
        ('platFee', 0),  # 平台费用
    )

    def _getcommission(self, size, price, pseudoexec):

        if size > 0:
            return max(size * price * self.p.commission, self.p.minCommission) + self.p.platFee
        elif size < 0:
            return max(abs(size) * price * self.p.commission, self.p.minCommission) + abs(
                size) * price * self.p.stampduty + self.p.platFee
        else:
            return 0
