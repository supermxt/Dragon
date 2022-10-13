import backtrader as bt


class KDJ(bt.Indicator):
    lines = ('K', 'D', 'J')

    params = (
        ('period', 9),
        ('period_dfast', 3),
        ('period_dslow', 3),
    )

    plotlines = dict(
        J=dict(
            _fill_gt=('K', ('red', 0.50)),
            _fill_lt=('K', ('green', 0.50)),
        )
    )

    def __init__(self):
        # Add a KDJ indicator
        # self.kd = bt.indicators.StochasticFull(
        #     self.data,
        #     period=self.p.period,
        #     period_dfast=self.p.period_dfast,
        #     period_dslow=self.p.period_dslow,
        # )
        self.kd = bt.talib.STOCH(df['high'].values,
                                 df['low'].values,
                                 df['close'].values,
                                 fastk_period=9,
                                 slowk_period=5,
                                 slowk_matype=1,
                                 slowd_period=5,
                                 slowd_matype=1)

        self.l.K = self.kd.percD
        self.l.D = self.kd.percDSlow
        self.l.J = self.K * 3 - self.D * 2
