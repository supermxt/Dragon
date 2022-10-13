import datetime as dt
import pandas as pd
import backtrader as bt
import StockCommissionScheme as scs
import PersonalStrategy as ps
import ExtendPandasData as epd
import os

StartTime = dt.datetime.now()

backtest_start_date = dt.datetime(2022, 1, 1)
backtest_end_date = dt.datetime(2022, 5, 1)
backtest_start_date_str = backtest_start_date.strftime('%Y-%m-%d')
backtest_end_date_str = backtest_end_date.strftime('%Y-%m-%d')

SampleSecurityCountLimit = 50
SkipSecurityCount = 0

cerebro = bt.Cerebro(tradehistory=True)

data_file_path = "D:/Projects/DownloadAllHistoryData/MinuteData/Data/MinuteData_2020_20220801/"
files = os.listdir(data_file_path)
filecount = 0
first_bar_date = ''
print(f'{dt.datetime.now()}：====开始读取数据===========')
for file in files:
    if not os.path.isdir(file):
        # if not file.startswith('605117'):
        #     continue
        if file.startswith('30'):
            continue
        if file.startswith('68'):
            continue
        filecount = filecount + 1
        if filecount > SampleSecurityCountLimit:
            break
        if filecount <= SkipSecurityCount:
            continue
        # print(f'{dt.datetime.now()}：====读取数据============{file}====={filecount}')
        df = pd.read_csv(data_file_path + file, index_col=0, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                         parse_dates=True, dtype={9: str, 10: str})
        # df['last_close'] = df['close'].shift(1)
        df = df[((backtest_start_date_str <= df.index) & (df.index <= backtest_end_date_str))]
        if len(df) == 0:
            continue
        if first_bar_date == '':
            first_bar_date = df.index.values[0]
        if df.index.values[0] != first_bar_date:
            continue
        security_code = df['code'].values[0]
        security_name = df['name'].values[0]
        if "ST" in security_name:
            continue
        df.index.rename('datetime', inplace=True)
        df.rename({'vol': 'volume'}, axis=1, inplace=True)
        df['quantity_relative_ratio'] = df['volume'] * 5 / (
                df['volume'].shift(1) + df['volume'].shift(2) + df['volume'].shift(3) + df['volume'].shift(4) + df[
            'volume'].shift(5))
        df = df[['open', 'high', 'low', 'close', 'volume', 'rise', 'quantity_relative_ratio',
                 'circulationequity']]

        data = epd.ExtendPandasData(dataname=df, name=security_code, plot=True, security_code=security_code,
                                    security_name=security_name)
        cerebro.adddata(data)

print(f'{dt.datetime.now()}：====开始设置策略参数===========')
print('==============================')
print(f'      股票池数量：{len(cerebro.datas)}')
StartCash = 100000000
cerebro.broker.setcash(StartCash)
print(f'       初始资金：{StartCash}元')
cerebro.broker.set_coc(True)
# cerebro.broker.orders.count()
transaction_value = 10000
print(f'    每笔交易金额：{transaction_value}元')
stamp_duty = 0.001
commission = 0.002
commission_start = 5
comminfo = scs.StockCommissionScheme(stampduty=stamp_duty, commission=commission,
                                     minCommission=commission_start)
cerebro.broker.addcommissioninfo(comminfo)
print(f'       印花税率：千分之{stamp_duty * 1000}')
print(f'       佣金比例：千分之{commission * 1000}')
print(f'       佣金起点：{commission_start}元')
buy_percent_low = 0.085
buy_percent_high = 0.095
sell_percent = -0.1
open_price_rising_percent_limit = 0.095
quantile_limit = 0.6
history_rising = 0.06
history_day_count = 2
start_hour = 10
start_minute = 30
end_hour = 11
end_minute = 30
buy_instant = True
cerebro.addstrategy(ps.RisingStrategy, buy_percent_low=buy_percent_low, buy_percent_high=buy_percent_high,
                    sell_percent=sell_percent, open_price_rising_percent_limit=open_price_rising_percent_limit,
                    quantile_limit=quantile_limit, history_day_count=history_day_count, start_hour=start_hour,
                    start_minute=start_minute, end_hour=end_hour,
                    end_minute=end_minute, transaction_value=transaction_value, buy_instant=buy_instant)
# print(f'   买入涨幅不低于：{buy_percent_low * 100}%')
# print(f'   买入涨幅不高于：{buy_percent_high * 100}%')
# print(f'起始时间涨幅不高于：{open_price_rising_percent_limit * 100}%')
# print(f'     卖出跌幅阈值：{sell_percent * 100}%')
# print(f'  价格不高于分位数：{quantile_limit}')
# print(f'  前{history_day_count}日涨幅不高于：{history_rising * 100}%')
# print(f'        时间范围：{start_hour}点{start_minute}分 -- {end_hour}点{end_minute}分 ')
# print('==============================')
# cerebro.optstrategy(MyStrategy,buy_percent=[0.08,0.06])
print(f'{dt.datetime.now()}：====开始初始化策略===============')
cerebro.run()
EndTime = dt.datetime.now()
print(f'=====总用时：{(EndTime - StartTime)}=======================================')
