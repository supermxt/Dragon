import backtrader as bt


class RSV(bt.Indicator):
    lines = ('rsv',)
    params = (('period', 9),)

    def __init__(self):
        self.addminperiod(self.params.period + 1)

    def next(self):
        close0 = self.data.close[0]
        low_n = min(self.data.low.get(size=self.params.period))
        high_n = max(self.data.high.get(size=self.params.period))
        rsv = (close0 - low_n) / (high_n - low_n) * 100
        self.lines.rsv[0] = rsv


class KDJ(bt.Indicator):
    lines = ('K', 'D', 'J', 'upperband', 'lowerband')

    params = (
        ('period_rsv', 9),
        ('period_k', 3),
        ('period_d', 3),
        ('myplot', False),
        ('upperband', 80),
        ('lowerband', 20),
    )

    # plotlines = dict(
    #     J=dict(
    #         _fill_gt=('K', ('red', 0.50)),
    #         _fill_lt=('K', ('green', 0.50)),
    #     )
    # )

    def __init__(self):
        min_period = self.params.period_rsv * self.params.period_k * self.params.period_d + 1
        self.addminperiod(min_period)
        self.plotinfo.plot = self.params.myplot

        rsv = RSV(self.data, period=self.params.period_rsv)
        self.line_k = bt.indicators.SmoothedMovingAverage(rsv, period=self.params.period_d)
        self.line_d = bt.indicators.SmoothedMovingAverage(self.line_k, period=self.params.period_d)
        self.line_j = self.line_k * 3 - self.line_d * 2

    def next(self):
        self.lines.K[0] = self.line_k[0]
        self.lines.D[0] = self.line_d[0]
        self.lines.J[0] = self.line_j[0]
        self.lines.upperband[0] = self.params.upperband
        self.lines.lowerband[0] = self.params.lowerband
