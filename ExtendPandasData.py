import backtrader as bt


class ExtendPandasData(bt.feeds.PandasData):
    lines = ('rise', 'quantity_relative_ratio', 'circulationequity')
    params = (
        ('rise', -1), ('quantity_relative_ratio', -1), ('circulationequity', -1),
        ('security_code', ''),
        ('security_name', ''),)

    def __init__(self):
        super(ExtendPandasData, self).__init__()
        self.security_code = self.params.security_code
        self.security_name = self.params.security_name
