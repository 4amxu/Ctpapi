"""
关注公众号: Ctp接口量化

"""

from Ctpapi import *
from Config import Config
class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["m2105","ni2104","rb2105","ag2106","IF2103","IC2103","i2105","j2105"]  #订阅合约
        self.bar_time = BarType.Min  #订阅K线周期  秒级 BarType.Time3  Time5  Time15  Time30       分钟级  BarType.Min、  Min3 、 Min5 、 Min15 、 Min30 、 Min60
        self.tick_time = 10  #砖型图tick数
        self.volume = {
        "m2105":{"总持仓":3,"止损":0,"止盈":0,"移动止损":0},
        "ni2104":{"总持仓":1,"止损":0,"止盈":0,"移动止损":0},
        "rb2105":{"总持仓":5,"止损":0,"止盈":0,"移动止损":0},
        "ag2106":{"总持仓":2,"止损":0,"止盈":0,"移动止损":0},
        "IF2103":{"总持仓":1,"止损":0,"止盈":0,"移动止损":0},
        "IC2103":{"总持仓":1,"止损":0,"止盈":0,"移动止损":0},
        "i2105":{"总持仓":5,"止损":0,"止盈":0,"移动止损":0},
        "j2105":{"总持仓":2,"止损":0,"止盈":0,"移动止损":0}}  #下单手数
    def on_trade(self, trade):
        print(trade)
    # def on_tick(self, tick=None):
        # print(tick.InstrumentID,tick.LastPrice)  
    def on_bar(self, tick=None, Bar=None):
        symbol = tick.InstrumentID   #合约代码
        Bid = tick.BidPrice1    #买价
        Ask = tick.AskPrice1    #卖价
        LastPrice = tick.LastPrice  #最新价
        print(Bar)
        Pos = self.GetPosition(symbol)     # 返回一条持仓
        # print(Pos)        
        # # # 开多单
        if Pos["方向"]=="None" and Bar['Direction'] == "Long":
            print("MACD策略开多")
            self.send(symbol, DirectionType.Buy, OffsetType.Open, Ask, self.volume[symbol]["总持仓"], OrderType.Limit)  # # OrderType.FOK """全部完成，否则撤销"""  OrderType.FAK """部分成交，剩余撤销"""  OrderType.Market 市价   OrderType.Limit 限价
        # # # 开空单
        if Pos["方向"]=="None" and Bar['Direction'] == "Short":
            print("MACD策略开空")
            self.send(symbol, DirectionType.Sell, OffsetType.Open, Bid, self.volume[symbol]["总持仓"], OrderType.Limit)   # # OffsetType.Open 开仓，   OffsetType.Close 平仓，   OffsetType.CloseToday 平今 ， OffsetType.CloseYesterday 平昨        
        # # # 平多单
        if Pos["方向"]=="Long" and Bar['Direction'] == "Short":
            self.send(symbol, DirectionType.Sell, OffsetType.Close, Bid, Pos["总持仓"], OrderType.Limit)   #    OffsetType.Close 已优化 适应 上期所 平今 平昨  的区别
            self.send(symbol, DirectionType.Sell, OffsetType.Open, Bid, self.volume[symbol]["总持仓"], OrderType.Limit)
        # # # 平空单        
        if Pos["方向"]=="Short" and Bar['Direction'] == "Long":
            self.send(symbol, DirectionType.Buy, OffsetType.Close, Ask, Pos["总持仓"], OrderType.Limit)
            self.send(symbol, DirectionType.Buy, OffsetType.Open, Ask, self.volume[symbol]["总持仓"], OrderType.Limit)
if __name__ == '__main__':
    t = CTP(MACDStrategy())
    t.Login(Config)
