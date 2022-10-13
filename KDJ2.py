import backtrader as bt

import talib
import numpy as np
from functools import reduce


def SMA_CN(close, timeperiod):
    close = np.nan_to_num(close)
    return reduce(lambda x, y: ((timeperiod - 1) * x + y) / timeperiod, close)


def MACD_CN(close, fastperiod, slowperiod, signalperiod):
    macdDIFF, macdDEA, macd = talib.MACDEXT(close, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod,
                                            slowmatype=1, signalperiod=signalperiod, signalmatype=1)
    macd = macd * 2
    return macdDIFF, macdDEA, macd


def RSI_CN(close, timeperiod):
    diff = map(lambda x, y: x - y, close[1:], close[:-1])
    diffGt0 = map(lambda x: 0 if x < 0 else x, diff)
    diffABS = map(lambda x: abs(x), diff)
    diff = np.array(diff)
    diffGt0 = np.array(diffGt0)
    diffABS = np.array(diffABS)
    diff = np.append(diff[0], diff)
    diffGt0 = np.append(diffGt0[0], diffGt0)
    diffABS = np.append(diffABS[0], diffABS)
    rsi = map(lambda x: SMA_CN(diffGt0[:x], timeperiod) / SMA_CN(diffABS[:x], timeperiod) * 100,
              range(1, len(diffGt0) + 1))

    return np.array(rsi)


def KDJ_CN(high, low, close, fastk_period, slowk_period, fastd_period):
    kValue, dValue = talib.STOCHF(np.array(high), np.array(low), np.array(close), fastk_period, fastd_period=1,
                                  fastd_matype=0)

    kValue = np.array(map(lambda x: SMA_CN(kValue[:x], slowk_period), range(1, len(kValue) + 1)))
    dValue = np.array(map(lambda x: SMA_CN(kValue[:x], fastd_period), range(1, len(kValue) + 1)))

    jValue = 3 * kValue - 2 * dValue

    func = lambda arr: np.array([0 if x < 0 else (100 if x > 100 else x) for x in arr])

    kValue = func(kValue)
    dValue = func(dValue)
    jValue = func(jValue)
    return kValue, dValue, jValue


class KDJ(bt.Indicator):
    lines = ('K', 'D', 'J')

    params = (('data',None),
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
        self.kd,self.ll= bt.talib.STOCH([self.params.data.high,
                                 self.params.data.low,
                                 self.params.data.close],
                                 fastk_period=9,
                                 slowk_period=3,
                                 slowk_matype=1,
                                 slowd_period=3,
                                 slowd_matype=1)

        self.l.K = self.kd.percD
        self.l.D = self.kd.percDSlow
        self.l.J = self.K * 3 - self.D * 2


class KDJ2(bt.Indicator):
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
        self.kd = bt.indicators.StochasticFull(
            self.data,
            period=self.p.period,
            period_dfast=self.p.period_dfast,
            period_dslow=self.p.period_dslow,
        )

        self.l.K = self.kd.percD
        self.l.D = self.kd.percDSlow
        self.l.J = self.K * 3 - self.D * 2
