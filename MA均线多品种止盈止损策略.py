"""
关注公众号: Ctp接口量化

"""
from _ctp import *
from Config import Config
class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["m2105","ni2104","rb2105","ag2106","IF2103","IC2103","i2105","j2105"]  #订阅合约
        self.bar_time = BarType.Time15  #订阅K线周期  秒级 BarType.Time3  Time5  Time15  Time30       分钟级  BarType.Min、  Min3 、 Min5 、 Min15 、 Min30 、 Min60
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
        # print(Bar[0]["symbol"]) #合约
        kline = Bar[0]["data"]    # K 线数据
        # if len(kline) <= 35:   # 小于35 条 退出 
            # return   
        # K,D,J  = self.KDJ(kline) # 取KDJ指标数组
        # UP,MB,DN  = self.BOLL(kline) # 取BOLL指标数组
        # EMA  = self.EMA(kline,60) # 取EMA指标数组
        # RSI  = self.RSI(kline) # 取RSI指标数组
        MA1  = self.MA(kline,30) # 取MA指标数组
        MA2  = self.MA(kline,60) # 取MA指标数组
        # dif,dea,macd  = self.MACD(kline) # 取MACD指标数组
        close,High,low = self.tick(kline)      # 取收盘价数组 # 获取最新价格（卖价）
        # print(self.Get_Position(symbol))      # 返回多条持仓
        Position = self.GetPosition(symbol)     # 返回一条持仓
        # print(Position)
        # print(self.GetData(symbol))   # 获取k历史数据
        # # 开多单
        # if Position["方向"]=="None" and MA1[-1] > MA2[-1] and MA1[-2] < MA2[-2]:
            # print("MACD策略开多")
            # self.send(symbol, DirectionType.Buy, OffsetType.Open, Ask, self.volume[symbol]["总持仓"], OrderType.Limit)  # # OrderType.FOK """全部完成，否则撤销"""  OrderType.FAK """部分成交，剩余撤销"""  OrderType.Market 市价   OrderType.Limit 限价
            # 最低价 = min(low[-10:])
            # self.volume[symbol]["移动止损"] = 最低价
            # self.volume[symbol]["止损"] = 最低价
            # self.volume[symbol]["止盈"] = Ask + (Ask-最低价)*3
        # # # # 开空单
        # if Position["方向"]=="None" and MA1[-1] < MA2[-1] and MA1[-2] > MA2[-2]:
            # print("MACD策略开空")
            # self.send(symbol, DirectionType.Sell, OffsetType.Open, Bid, self.volume[symbol]["总持仓"], OrderType.Limit)   # # OffsetType.Open 开仓，   OffsetType.Close 平仓，   OffsetType.CloseToday 平今 ， OffsetType.CloseYesterday 平昨
            # 最高价 = max(High[-10:])
            # self.volume[symbol]["移动止损"] = 最高价
            # self.volume[symbol]["止损"] = 最高价
            # self.volume[symbol]["止盈"] = Bid - (最高价-Bid)*3            
        # # # # 平多单
        # if Position["方向"]=='Long' and LastPrice <= self.volume[symbol]["移动止损"] and self.volume[symbol]["移动止损"] != 0 or Position["方向"]=="Long" and MA1[-1] < MA2[-1] and MA1[-2] > MA2[-2] or Position["方向"]=="Long" and self.volume[symbol]["止损"] !=0 and LastPrice <= self.volume[symbol]["止损"] or Position["方向"]=="Long" and self.volume[symbol]["止损"] !=0 and LastPrice >= self.volume[symbol]["止盈"]:
            # self.send(symbol, DirectionType.Sell, OffsetType.Close, Bid, Position["总持仓"], OrderType.Limit)   #    OffsetType.Close 已优化 适应 上期所 平今 平昨  的区别   
            # self.volume[symbol]["止损"] = 0
            # self.volume[symbol]["止盈"] = 0
            # self.volume[symbol]["移动止损"] = 0            
        # # # # 平空单        
        # if Position["方向"]=='Long' and LastPrice >= self.volume[symbol]["移动止损"] and self.volume[symbol]["移动止损"] != 0 or Position["方向"]=="Short" and MA1[-1] > MA2[-1] and MA1[-2] < MA2[-2] or Position["方向"]=="Short" and self.volume[symbol]["止损"] !=0 and LastPrice >= self.volume[symbol]["止损"] or Position["方向"]=="Short" and self.volume[symbol]["止损"] !=0 and LastPrice <= self.volume[symbol]["止盈"]:
            # self.send(symbol, DirectionType.Buy, OffsetType.Close, Ask, Position["总持仓"], OrderType.Limit)
            # self.volume[symbol]["止损"] = 0
            # self.volume[symbol]["止盈"] = 0 
            # self.volume[symbol]["移动止损"] = 0 
        # # # 多单 修改移动止损价
        # if Position["方向"]=='Long' and (LastPrice - self.volume[symbol]["移动止损"]) > (Position["开仓价"] - self.volume[symbol]["止损"]):
            # self.volume[symbol]["移动止损"] = LastPrice - (Position["开仓价"] - self.volume[symbol]["止损"])
            # print("多单 修改移动止损价",self.volume[symbol]["移动止损"])

        # # # 空单 修改移动止损价
        # if Position["方向"]=='Short' and (self.volume[symbol]["移动止损"] - LastPrice) > (self.volume[symbol]["止损"] - Position["开仓价"]):
            # self.volume[symbol]["移动止损"] = LastPrice + (self.volume[symbol]["止损"] - Position["开仓价"])
            # print("空单 修改移动止损价",self.volume[symbol]["移动止损"])


if __name__ == '__main__':
    t = CTP(MACDStrategy())
    t.Login(Config)
