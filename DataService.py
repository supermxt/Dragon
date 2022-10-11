def GetSecurityListFromTDX(api=None):
    import pandas as pd

    # 如果没有提供通达信连接，则自己生成一个连接
    if api is None:
        from pytdx.hq import TdxHq_API
        api_inner = TdxHq_API()
        api_inner.connect('119.147.212.81', 7709)
    else:
        api_inner = api

    # 循环深圳(code 0)、上海(code 1)两个市场，按每页1000条（通达信上限），获取所有股票信息
    TotalDFList = []
    for MarketCode in [0, 1]:
        PageCount = 0
        while True:
            TempDF = api_inner.to_df(api_inner.get_security_list(MarketCode, PageCount * 1000))
            TempDF['market'] = MarketCode
            TotalDFList.append(TempDF)
            PageCount = PageCount + 1
            if len(TempDF) == 0:
                break
    TotalDF = pd.concat(TotalDFList, axis=0, ignore_index=True)

    # 股票信息存在大量无关条目，按开头数字筛选出所需股票
    DF0 = TotalDF[(TotalDF['code'].str.startswith('0', na=False)) & (TotalDF['market'] == 0)]
    DF1 = TotalDF[(TotalDF['code'].str.startswith('30', na=False)) & (TotalDF['market'] == 0)]
    DF2 = TotalDF[(TotalDF['code'].str.startswith('6', na=False)) & (TotalDF['market'] == 1)]
    DF_TEMP = pd.concat([DF0, DF1, DF2], axis=0, ignore_index=True)[:]

    # 仅保留两个字段
    DF_TEMP = DF_TEMP[['code', 'name']]

    # 如果是新生成的连接，断掉
    if api is None:
        api_inner.disconnect()

    return DF_TEMP


def GetSecurityMarket(code):
    if code.startswith('6'):
        security_market = 1
    else:
        security_market = 0
    return security_market


def GetSecurityListFromGUGU():
    import requests
    import json
    import pandas as pd

    # GUGUData的付费Token
    url = "https://api.gugudata.com/stock/cn/realtime?appkey=FFEULB5CC3QX"

    # 读取当前全市场实时股票行情，失败则重试，直到成功
    while True:
        Response = requests.request("GET", url, headers={}, data={})
        ResponseText = json.loads(Response.text)
        DataStatus = ResponseText['DataStatus']
        StatusCode = DataStatus['StatusCode']
        ResponseDateTime = DataStatus['ResponseDateTime']
        DataTotalCount = DataStatus['DataTotalCount']
        if StatusCode == 100:
            break
    RealTimeData = ResponseText['Data']

    # 循环读取数据，存入并整合为一个Dataframe
    df = []
    for i in range(0, DataTotalCount):
        df.append(pd.DataFrame.from_dict(RealTimeData[i], orient='index').T)
    df = pd.concat(df, ignore_index=True)

    # 整理Dataframe的结构
    df.rename(columns={'Symbol': 'code',
                       'StockName': 'name'}, inplace=True)
    # df['servertime'] = ResponseDateTime[-8:]
    # df['open'] = pd.to_numeric(df['Open']).fillna(0)
    # df['price'] = pd.to_numeric(df['Latest']).fillna(0)
    # df['last_close'] = pd.to_numeric(df['PreClose']).fillna(0)
    # df['volume'] = pd.to_numeric(df['TradingVolume']).fillna(0)
    # df['amount'] = pd.to_numeric(df['TradingAmount']).fillna(0)
    # df = df.round(2)
    # df['rise'] = pd.to_numeric(df['ChangePercent']).fillna(0) / 100
    # df = df[['servertime', 'code', 'name', 'open', 'price', 'last_close', 'rise', 'volume', 'amount']][:]

    # 删除4和8开头的股票
    df = df[(~df['code'].str.startswith('8'))]
    df = df[(~df['code'].str.startswith('4'))]
    # 此处只需返回code段
    df = df[['code', 'name']]
    return df


def GetCirculationMarketValue(security_code, api=None):
    # 如果没有提供通达信连接，则自己生成一个连接
    if api is None:
        from pytdx.hq import TdxHq_API
        api_inner = TdxHq_API()
        api_inner.connect('119.147.212.81', 7709)
    else:
        api_inner = api
    circulation_market_value=0
    security_market = GetSecurityMarket(security_code)
    df = api_inner.to_df(api_inner.get_finance_info(security_market, security_code))
    circulation_equity = df['liutongguben'].tolist()[0] / 10000 / 10000
    df = api_inner.to_df(api.get_security_bars(9, security_market, security_code, 0, 1))
    current_price = df['close'].tolist()[0]
    circulation_market_value = current_price * circulation_equity
    # 如果是新生成的连接，断掉
    if api is None:
        api_inner.disconnect()

    return circulation_market_value


def GetOpenRiseRate(security_code, history_day_count, api=None):
    # 如果没有提供通达信连接，则自己生成一个连接
    if api is None:
        from pytdx.hq import TdxHq_API
        api_inner = TdxHq_API()
        api_inner.connect('119.147.212.81', 7709)
    else:
        api_inner = api
    security_market = GetSecurityMarket(security_code)
    df = api_inner.to_df(api.get_security_bars(9, security_market, security_code, history_day_count, 2))
    current_open = df['open'].tolist()[-1]
    last_close = df['close'].tolist()[-2]
    open_rise_rate = current_open / last_close - 1

    # 如果是新生成的连接，断掉
    if api is None:
        api_inner.disconnect()

    return open_rise_rate


def GetMinuteData(security_code, date_str, api=None):
    # 如果没有提供通达信连接，则自己生成一个连接
    if api is None:
        from pytdx.hq import TdxHq_API
        api_inner = TdxHq_API()
        api_inner.connect('119.147.212.81', 7709)
    else:
        api_inner = api
    security_market = GetSecurityMarket(security_code)
    df = api_inner.to_df(api.get_history_minute_time_data(security_market, security_code, date_str))

    # 如果是新生成的连接，断掉
    if api is None:
        api_inner.disconnect()

    return df
