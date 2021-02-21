class Strategy():
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["ni2109","sc2109","ag2109"]  #订阅合约
        self.BarType = BarType.Min  #K线周期以秒计
        self.tick_time = 10  #砖型图tick数
        self.data = []
        self.position = []
    def GetPosition(self, symbol=None):
        for i in self.position:
            if symbol==i['合约']:
                return i
                break
        else:
            # print('该合约没有持仓')
            Position = {"合约":0,"盈亏":0,"持仓成本":0,"总持仓":0,"今仓":0,"昨仓":0,"方向":"None","开仓价":0}
            return Position
    def on_tick(self, tick):
        pass
    def on_bar(self, tick=None, bar=None):
        pass
    def on_order(self, order):
        pass
    def on_position(self, positions):
        pass
    def on_trade(self, trade):
        pass
    def on_account(self, account):
        pass
    def on_Instrument(self, Instrument):
        pass
###############################################################################################
    def send(self, symbol, Direction, Offset, Price, volume, PriceType):   #报单
        self.TD_Api.send(symbol, Direction, Offset, Price, volume, PriceType) 
    def SubMarketData(self, sub_lsit):
        print (sub_lsit)
        self.MD_Api.SubMarketData(sub_lsit)
    # @staticmethod
    def setTraderSpi(self, TDApi):
        self.TD_Api = TDApi
    # @staticmethod    
    def setMDSpi(self, MDApi):
        self.MD_Api = MDApi

class CTP():
    def __init__(self,Strategy_demo):
        self.Strategy_demo = Strategy_demo
    def Login(self, setting):
        tdspi=TdSpi(setting,self.Strategy_demo)
        mdspi=MdSpi(setting,self.Strategy_demo)
