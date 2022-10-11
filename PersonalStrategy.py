import backtrader as bt
import datetime as dt
import numpy as np
import pandas as pd


class RisingStrategy(bt.Strategy):
    params = dict(
        buy_percent_low=0.08,
        buy_percent_high=0.095,
        sell_percent=-0.05,
        open_price_rising_percent_limit=0.05,
        quantile_limit=0.5,
        history_rising=0.5,
        history_day_count=2,
        transaction_value=10000,
        start_hour=9,
        start_minute=30,
        end_hour=9,
        end_minute=33,
        buy_instant=True,
        printlog=True,
    )

    def __init__(self):

        print(f'{dt.datetime.now()}：====开始回测===========')
        # 记录胜负交易数量
        self.count_win = 0
        self.count_lose = 0

        # 设置布林线高线和低线指标，以及20日均线指标
        self.boll_upper = {}
        self.boll_middle = {}
        self.boll_lower = {}
        self.ma20 = {}
        for data in self.datas:
            self.boll_upper[data.security_code] = bt.indicators.BollingerBands(data, period=20).top
            self.boll_middle[data.security_code] = bt.indicators.BollingerBands(data, period=20).mid
            self.boll_lower[data.security_code] = bt.indicators.BollingerBands(data, period=20).bot
            self.ma20[data.security_code] = bt.indicators.SMA(data, period=10)

        # 取得初始现金数量
        self.start_cash = self.cerebro.broker.getcash()

        # 设置交易和收益两个日志文件
        self.log_file_for_trade = open(f'log/{dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}_trade.csv',
                                       encoding='gb2312',
                                       mode='w')
        self.log_file_for_profit = open(f'log/{dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}_profit.csv',
                                        encoding='gb2312',
                                        mode='w')

    def next(self):

        # 回测第一天执行
        if len(self) == 1:
            pass

        for data in self.datas:
            # 获取各项指标
            current_bar_index = len(self)
            security_code = data.security_code
            security_name = data.security_name
            current_date = data.datetime.date(0)
            current_open = data.open[0]
            current_high = data.high[0]
            current_low = data.low[0]
            current_close = data.close[0]
            current_volume = data.volume[0]
            current_rise = data.rise[0]
            current_circulationequity = data.circulationequity[0]
            current_circulation_value = current_circulationequity * current_close / 100000000
            current_turnover_rate = current_volume * 100 / current_circulationequity
            last_close = data.close[-1]
            last_high = data.high[-1]
            last_rise = data.rise[-1]
            current_position = self.cerebro.broker.getposition(data)
            current_quantity_relative_ratio = data.quantity_relative_ratio[0]
            # print(f'第{current_bar_index}天， {current_date} {security_code}, {security_name} ')

            # # 检查期间是否是增长，如果增长则打印
            # if  current_bar_index == data.buflen() and current_close>data.close[-data.buflen()+1]:
            #
            #     print(f'{security_code},{current_circulation_value}')

            # if current_bar_index < 25:
            #     continue
            # volume_5_days_before = list(data.volume.get(ago=-1, size=5))
            # if len(volume_5_days_before) < 5:
            #     continue
            # # if sum(volume_5_days_before) ==0:
            # #     print(f'{security_code} {current_date} {volume_5_days_before}')
            # volume_ratio = current_volume / (sum(volume_5_days_before) / 5)

            if current_position.size > 0:
                sell_flag = 0
                sell_reason = ''

                # if (current_position.price * 1.1 < current_position.adjbase):
                #     sell_flag=1
                current_trade = list(self._trades[data].values())[0][-1]
                # print(current_trade.open_datetime().strftime("%Y-%m-%d"))
                # print(current_trade.baropen,current_bar_index)
                # if current_bar_index-current_trade.baropen == 3:
                #     sell_flag = 1

                # 跌超过5%止损
                if (current_close / current_position.price) < 0.95:
                    sell_flag = 1
                    sell_reason = sell_reason + f'损失：{current_close / current_position.price:.2f} '

                # if (current_turnover_rate > 0.03):
                #     sell_flag = 1
                #     sell_reason = sell_reason + f'换手率：{current_turnover_rate:.2f} '
                #
                # # 检查量比大于2
                # if (current_quantity_relative_ratio > 2):
                #     sell_flag = 1
                #     sell_reason = sell_reason + f'量比：{current_quantity_relative_ratio:.2f} '

                if (data.close[0] < self.boll_upper[security_code][0]) and (
                        data.high[-1] >= self.boll_upper[security_code][-1]) and (
                        data.high[-2] >= self.boll_upper[security_code][-2]):
                    sell_flag = 1
                    sell_reason = sell_reason + f'布林线：收盘价{current_close} 低于布林高线{self.boll_upper[security_code][0]:.2f} '

                if sell_flag == 0:
                    continue

                # print(
                # f'sell {security_code}  {(current_position.price * 1.1 < current_position.adjbase)} {current_turnover_rate > 0.03} {current_close >= self.bolltop[security_code][0] * 1.1} {self.bolltop[security_code][0]}')
                self.order = self.sell(data=data, size=current_position.size, tradeid=int(security_code))
                self.order.addinfo(security_code=security_code, security_name=security_name, sell_date=current_date,
                                   sell_reason=sell_reason)
                # continue

            if current_position.size == 0:

                # # 检查流通市值小于200亿
                # if current_circulation_value > 200 :
                #     continue

                # # 检查历史30天最低量
                # check_volume_history_day_count = 30
                # if current_bar_index < check_volume_history_day_count:
                #     continue
                # check_volume_list = data.volume.get(ago=0, size=check_volume_history_day_count)
                # if len(check_volume_list) == 0:
                #     continue
                # if data.volume[0] > min(check_volume_list):
                #     continue

                # # 检查近10天是否有涨停
                # is_rised=False
                # for i in range(10):
                #     if data.rise[-i-1]>0.09:
                #         is_rised=True
                #         break
                # if not is_rised:
                #     continue

                # # 检查之前连续涨停不少于3天
                # before_day_index = -1
                # while data.rise[before_day_index] >= 0:
                #     before_day_index = before_day_index - 1
                # if (-before_day_index) <= 3:
                #     continue

                # # 检查更早的20天，为最低点
                # check_history_length = 30
                # total_history_length = check_history_length + (-before_day_index) + 1
                # if current_bar_index < total_history_length:
                #     continue
                # check_close_list = data.close.get(ago=before_day_index, size=check_history_length)
                # if len(check_close_list) == 0:
                #     continue
                # if data.close[before_day_index] > min(check_close_list):
                #     continue

                # 连续三天低于布林线低线
                if np.isnan(self.boll_lower[security_code][-3]):
                    continue
                if data.close[0] <= self.boll_lower[security_code][0]:
                    continue
                if data.low[-1] > self.boll_lower[security_code][-1] * 1:
                    continue
                if data.low[-2] > self.boll_lower[security_code][-2] * 1:
                    continue
                if data.low[-3] > self.boll_lower[security_code][-3] * 1:
                    continue

                #
                # print(
                #     f'{current_bar_index} {current_date} {security_code} {data.low[-1]}/{self.boll_lower[security_code][-1]} {data.low[-2]}/{self.boll_lower[security_code][-2]}  {data.low[-3]}/{self.boll_lower[security_code][-3]}')

                # 检查布林线宽度
                # boll_volatility = (self.boll_upper[security_code][0] - self.boll_lower[security_code][0]) / \
                #                   self.boll_middle[security_code][0]
                # if boll_volatility < 0.1:
                #     continue
                # if (data.close[-1] >= self.boll_lower[security_code][-1]*1.03) or (data.close[-2] >= self.boll_lower[security_code][-2]*1.03):
                #     continue

                # 检查量比大于2
                if current_quantity_relative_ratio < 2:
                    continue

                # # 检查分时图45度上涨，并且之后一直高于均线
                # data_file_path = "D:/Projects/DownloadAllHistoryData/MinuteData/Data/MinuteData_2020_20220801/"
                # df = pd.read_csv(data_file_path + security_code + '.csv', index_col=0, parse_dates=True,
                #                  dtype={9: str, 10: str})
                # df['last_close'] = df['close'].shift(1)
                # df = df[(pd.to_datetime(current_date) == df.index)]
                # current_price_list = []
                # for i in range(0, 239):
                #     current_price_list.append(df[f'price_{i}'].values[0])
                # current_volume_list = []
                # current_total_volume_list = []
                # current_value_list = []
                # current_total_value_list = []
                # current_average_price_list = []
                # for i in range(0, 239):
                #     current_volume_list.append(df[f'volume_{i}'].values[0])
                #     current_total_volume_list.append(sum(current_volume_list))
                #     current_value_list.append(current_volume_list[i] * current_price_list[i])
                #     current_total_value_list.append(sum(current_value_list))
                #     current_average_price_list.append(current_total_value_list[i] / current_total_volume_list[i])
                # # for i in  range(0, 239):
                # #     print(f'{current_price_list[i]}   {current_volume_list[i]}   {current_total_volume_list[i]}  {current_total_value_list[i]}  {current_average_price_list[i]}')
                #
                # rising_selected = False
                # for i in range(60, 239 - 40):
                #     check_rising_price_list = current_price_list[i:i + 40]
                #     fitting_line_rising_ratio = np.polyfit(range(0, 40), check_rising_price_list, 1)[0]
                #     if security_code=='000049' and pd.to_datetime(current_date).strftime('%Y-%m-%d')=='2022-04-27':
                #         print(f'{i} {fitting_line_rising_ratio} {current_price_list[i]}')
                #     if fitting_line_rising_ratio > 0.01 and max(check_rising_price_list) / last_close > 1.03:
                #         # if fitting_line_rising_ratio > 0.025:
                #         #     rising_selected = False
                #         #     break
                #         rising_selected = True
                #         # print(f'{current_date}  {security_code}  {security_name}  {i}  {fitting_line_rising_ratio}')
                # for j in range(i, 239):
                #     if rising_selected and current_price_list[j] <= current_average_price_list[j]:
                #         rising_selected = False
                #         break
                # if not rising_selected:
                #     continue
                # print(
                #         f'                                                                                                                     选中：{current_date} {security_code}, {security_name} ')

                # 检查前3天涨幅斜率不低于0.08
                # z1 = np.polyfit([1, 2, 3], [data.close[-3], data.close[-2], data.close[-1]], 1)
                # # print(f'xie{z1[0]} {data.close[-3]} {data.close[-2]} {data.close[-1]} {security_code}')
                # if z1[0] <= 0.08:
                #     continue

                # 检查前两天涨幅斜率不低于0.05
                # z2 = np.polyfit([1, 2], [data.close[-2], data.close[-1]], 1)
                # if z2[0] <= 0.05:
                #     continue

                # 检查前几天的均线，不能是下跌的
                # z3 = np.polyfit([1, 2, 3, 4], [self.ma20[security_code][-6], self.ma20[security_code][-4],
                #                                self.ma20[security_code][-2],
                #                                self.ma20[security_code][0]], 1)

                # 检查前几天的布林线中线，不能是下跌的
                # # z3 = np.polyfit([1, 2, 3], [self.boll_middle[security_code][-2],
                # #                             self.boll_middle[security_code][-1],
                # #                             self.boll_middle[security_code][0]], 1)
                # if z3[0] <= -0.02:
                #     continue

                # 检查历史30天，价格分位数不高于0.3
                # z4 = np.quantile(data.close.get(ago=0, size=30), 0.3)
                # if current_close > z4:
                #     continue

                # 检查前20天，一直是下降的
                # check_end_day_index = -4
                # check_start_day_index = check_end_day_index - 20
                # check_close_list = data.close.get(ago=check_end_day_index, size=20)
                # if len(check_close_list) == 0:
                #     continue
                # if data.close[check_end_day_index] > min(check_close_list):
                #     continue

                # 检查前低点是否突破布林线下线
                # # print(f'---------------{security_code}---{current_date}---{self.bollbot[security_code][0]}')
                # if data.close[check_end_day_index] >= self.boll_lower[security_code][check_end_day_index]:
                #     continue

                # 检查换手率，大于5%则排除
                # if (current_turnover_rate > 0.05):
                #     continue

                # 检查前10天量，是否是最低
                # check_volume_list = data.volume.get(ago=check_end_day_index, size=10)
                # if len(check_volume_list)==0:
                #     continue
                # if data.volume[check_end_day_index] > min(check_volume_list):
                #     continue

                # 执行买入
                if self.cerebro.broker.getcash() >= self.params.transaction_value:
                    size = int(self.params.transaction_value / 100 / current_close) * 100
                else:
                    size = int(self.cerebro.broker.getcash() / 100 / current_close) * 100
                if size == 0:
                    print(f'资金不足{security_code} {security_name} {current_close}')
                    continue
                self.order = self.buy(data=data, size=size, tradeid=int(security_code))
                self.order.addinfo(security_code=security_code, security_name=security_name, buy_date=current_date)
                # print(
                #     f'{current_date} 第{current_bar_index}天 买{security_code} {security_name} 连涨{-before_day_index - 1}天 波动率{boll_volatility:.2f}')
                # print(f'xie z3 {security_code} {z3[0]}')

        # 回测一天结束后执行

        # 计算收益，记录日志并打印
        start_cash = self.start_cash
        current_cash = self.cerebro.broker.getcash()
        current_value = self.cerebro.broker.getvalue()
        stock_value = current_value - current_cash
        net_profit = current_value - start_cash
        if current_value != current_cash:
            profit_ratio = (current_value - start_cash) / (current_value - current_cash) * 100
        else:
            profit_ratio = 0
        if (self.count_win + self.count_lose) > 0:
            win_ratio = self.count_win / (self.count_win + self.count_lose)
        else:
            win_ratio = 0
        self.log_file_for_profit.writelines(
            f'{current_date},{start_cash:.2f},{current_value:.2f},{current_cash:.2f},{stock_value:.2f},{net_profit:.2f},{profit_ratio:.2f},{win_ratio:.2f}\n')
        print(
            f'{current_date},开始资产：{round(start_cash, 2)},当前资产：{round(current_value, 2)},现金资产：{round(current_cash, 2)},股票资产：{round(stock_value, 2)},净收益：{round(net_profit, 2)},收益率：{round(profit_ratio, 2)}%,胜率：{win_ratio:.2f}')

        # 打印持仓
        for data in self.datas:
            p = self.cerebro.broker.getposition(data)
            if p.size != 0:
                pass
                print(
                    f'           持有：{data._name} {p.size}股 平均成本{round(p.price, 2)}元 当前价格{round(p.adjbase, 2)}元 当前价值{round(p.adjbase * p.size, 2)}元 收益{round((p.adjbase - p.price) * p.size, 2)}元')

        # 全部回测结束时执行
        if current_bar_index == data.buflen():
            self.log_file_for_trade.close()
            self.log_file_for_profit.close()

    def log(self, log_text, log_date=None):
        if log_date == None:
            log_date = self.datas[0].datetime.date(0)
        print(f'{log_date.strftime("%Y-%m-%d")}：{log_text}')

    def notify_order(self, order):
        if order.status in [order.Submitted]:
            return
        if order.status in [order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'    买单  {order.info.security_code},{order.info.security_name},价格:{order.executed.price:.2f},份额:{order.executed.size},金额:{order.executed.size * order.executed.price:.2f},成本:{order.executed.value:.2f},手续费:{order.executed.comm:.2f}',
                    log_date=order.info.buy_date)
            else:
                self.log(
                    f'    卖单  {order.info.security_code},{order.info.security_name},价格:{order.executed.price:.2f},份额:{-order.executed.size},金额:{-order.executed.size * order.executed.price:.2f},成本:{order.executed.value:.2f},手续费：{order.executed.comm:.2f},原因：{order.info.sell_reason}',
                    log_date=order.info.sell_date)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(
            f'    交易关闭：股票代码：{trade.data.security_code}，股票名称：{trade.data.security_name}，买入日期：{trade.open_datetime().strftime("%Y-%m-%d")}，卖出日期：{trade.close_datetime().strftime("%Y-%m-%d")},持有{round(trade.barlen)}天,净收益：{trade.pnlcomm:.2f}',
            log_date=None)
        self.log_file_for_trade.writelines(
            f"{trade.data.security_code},{trade.open_datetime().strftime('%Y-%m-%d')},{trade.close_datetime().strftime('%Y-%m-%d')},{round(trade.barlen)},{trade.pnlcomm:.2f}\n")
        if trade.pnlcomm > 0:
            self.count_win = self.count_win + 1
        else:
            self.count_lose = self.count_lose + 1
