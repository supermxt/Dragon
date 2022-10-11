import DataService
import pandas as pd
import datetime as dt
from pytdx.hq import TdxHq_API

check_date_str=''

history_day_count = 0
debug_code = ''

# 建立通达信连接
api = TdxHq_API()
if api.connect(ip='119.147.212.81', port=7709):

    # 获取全市场股票清单
    code_list = DataService.GetSecurityListFromTDX(api)

    # 遍历清单，逐个股票筛选
    for idx in code_list.index:

        # 获取股票代码、所在市场代码、股票名称
        security_code = code_list['code'][idx]
        if security_code.startswith('30'):
            continue
        if security_code.startswith('68'):
            continue
        security_market = DataService.GetSecurityMarket(security_code)
        security_name = code_list['name'][idx]


        # 获取最近12天K线数据，如果不够最少11天，则跳过该股
        df = api.to_df(api.get_security_bars(9, security_market, security_code, history_day_count, 10 + 3))
        if security_code == debug_code:
            print(df)
        if len(df) < 13:
            # print(f'剔除 {security_code}, {security_name} : 数据不够10天')
            continue
        # 获取当前日期，转变格式
        current_date = pd.to_datetime(df['datetime']).dt.date.tolist()[-1]
        current_date_str = dt.date.strftime(current_date, '%Y%m%d')
        last_close_before_current = df['close'].tolist()[-2]

        # 计算每日涨幅
        df['last_close'] = df['close'].shift(1)
        df['rise'] = df['close'] / df['last_close'] - 1

        # if security_code=='000882':
        #     print(df)
        #     exit()

        last_rise=df['rise'].values[-3]
        if last_rise<0.085:
            # print(f'剔除 {security_code}, {security_name} : 前一天没有大涨')
            continue

        # 获取最后3天的收盘价，计算波动范围，超出平台期范围（4%）的股票，跳过
        last_n_day_close_list = df.tail(13)['close'].values[:-3]
        floating_ratio_range = max(last_n_day_close_list) / min(last_n_day_close_list) - 1
        if floating_ratio_range > 0.1:
            print(f'剔除 {security_code}, {security_name} : 没有达到平台期，近期波动 {round(floating_ratio_range * 100, 2)}%')
            continue

        current_rise=df['rise'].values[-1]+df['rise'].values[-2]
        if current_rise > -0.04:
            print(f'剔除 {security_code}, {security_name} : 没有回踩到位，当前涨幅 {round(current_rise * 100, 2)}%')
            continue

        print(f'{security_code}, {security_name} : 当前涨幅 {round(current_rise * 100, 2)}%')