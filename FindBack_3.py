import DataService
import pandas as pd
import datetime as dt
from pytdx.hq import TdxHq_API

rise_up_ratio_threshold = 0.085
rise_up_check_day_total_number = 2
trend_stable_check_day_count = 10
floating_ratio_threshold = 0.1
current_rise_up_ratio_threshold=-0.04

# 建立通达信连接
api = TdxHq_API()
if api.connect(ip='39.98.234.173', port=7709):

    # 获取全市场股票清单
    code_list = DataService.GetSecurityListFromTDX(api)

    # 删除30和68开头的股票
    code_list = code_list[(~code_list['code'].str.startswith('30'))]
    code_list = code_list[(~code_list['code'].str.startswith('68'))]

    # 遍历清单，逐个股票筛选
    for idx in code_list.index:

        # 获取股票代码、所在市场代码、股票名称
        security_code = code_list['code'][idx]
        security_market = DataService.GetSecurityMarket(security_code)
        security_name = code_list['name'][idx]

        # 获取最近K线数据，如果不够最少天，则跳过该股
        get_day_count = trend_stable_check_day_count + 1 + rise_up_check_day_total_number
        df = api.to_df(api.get_security_bars(9, security_market, security_code, 0, get_day_count))
        if len(df) < get_day_count:
            # print(f'剔除 {security_code}, {security_name} : 数据不够')
            continue

        # 计算每日涨幅
        df['last_close'] = df['close'].shift(1)
        df['rise'] = df['close'] / df['last_close'] - 1
        for rise_up_check_day_number in range(1, rise_up_check_day_total_number + 1):

            # 检查是否存在异常涨幅，没有则剔除
            rise_up_check_rise_ratio = df['rise'].values[-1 * (rise_up_check_day_number + 1)]
            if rise_up_check_rise_ratio < rise_up_ratio_threshold:
                # print(f'剔除 {security_code}, {security_name} : 前一天没有大涨')
                continue

            # 计算波动范围，不够稳定的股票，剔除
            last_n_day_close_list = df['close'].values[
                                    -1 * (trend_stable_check_day_count + 1 + rise_up_check_day_number):-1 * (
                                            rise_up_check_day_number + 1)]
            floating_ratio_range = max(last_n_day_close_list) / min(last_n_day_close_list) - 1
            if floating_ratio_range > floating_ratio_threshold:
                # print(f'剔除 {security_code}, {security_name} : 没有达到平台期，近期波动 {round(floating_ratio_range * 100, 2)}%')
                continue

            current_rise = df['close'].values[-1] /df['close'].values[-1 * (
                                            rise_up_check_day_number + 1)]-1
            if current_rise > current_rise_up_ratio_threshold:
                # print(f'剔除 {security_code}, {security_name} : 没有回踩到位，当前涨幅 {round(current_rise * 100, 2)}%')
                continue

            print(f'                                                      买入{security_code}, {security_name} : 近{rise_up_check_day_number}天涨幅 {round(current_rise * 100, 2)}%')
