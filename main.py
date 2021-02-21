from Ctpapi import *

class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["ni2103","rb2105","ag2102","IF2103","IC2103","i2109","jm2109"]  #订阅合约
        self.BarType = BarType.Time3  #订阅K线周期  秒级 BarType.Time3  Time5  Time15  Time30       分钟级  BarType.Min、  Min3 、 Min5 、 Min15 、 Min30 、 Min60
        self.volume = {"ni2103":5,"rb2105":3,"ag2102":2,"IF2103":3,"IC2103":2,"i2109":3,"jm2109":2}  #下单手数
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
        if len(kline) <= 35:   # 小于35 条 退出 
            return   
        K,D,J  = self.KDJ(kline) # 取KDJ指标数组
        UP,MB,DN  = self.BOLL(kline) # 取BOLL指标数组
        EMA  = self.EMA(kline,60) # 取EMA指标数组
        RSI  = self.RSI(kline) # 取RSI指标数组
        MA1  = self.MA(kline,30) # 取MA指标数组Channels
        MA2  = self.MA(kline,60) # 取MA指标数组Channels
        dif,dea,macd  = self.MACD(kline) # 取MACD指标数组
        close,High,low = self.tick(kline)      # 取收盘价数组 # 获取最新价格（卖价）
        # print("K线收盘价",close[-1])     # 取最新K线 收盘价
        # print("dif",dif[-2:])        # 显示10个 dif 元素
        # print("dea",dea[-2:])         # 显示10个 dea 元素
        # print("macd",macd[-2:])        # 显示10个 macd 元素
        # print("K",K[-2:])        # 显示10个 dif 元素
        # print("D",D[-2:])         # 显示10个 dea 元素
        # print("J",J[-2:])        # 显示10个 macd 元素
        # print("EMA",EMA[-2:])        # 显示10个 dif 元素
        # print("RSI",RSI[-2:])         # 显示10个 dea 元素
        # print("MA1",MA1[-2:])        # 显示10个 macd 元素 
        # print("MA2",MA2[-2:])        # 显示10个 macd 元素         
        # print("UP",UP[-2:])        # 显示10个 dif 元素
        # print("MB",MB[-2:])         # 显示10个 dea 元素
        # print("DN",DN[-2:])        # 显示10个 macd 元素
        # print(self.Get_Position(symbol))
        Position = self.GetPosition(symbol)
        print(Position)
        # print(self.GetData(symbol))
        # # 开多单
        if Position["方向"]=="None" and dif[-1]>dea[-1] and dif[-2] < dea[-2] and dea[-1] > 0:
            print("MACD策略开多")
            self.send(symbol, DirectionType.Buy, OffsetType.Open, Ask, self.volume[symbol], OrderType.Limit)  # # OrderType.FOK   OrderType.FAK   OrderType.Market
        # # # 开空单
        if Position["方向"]=="None" and dif[-1]<dea[-1] and dif[-2] > dea[-2] and dea[-1] < 0:
            print("MACD策略开空")
            self.send(symbol, DirectionType.Sell, OffsetType.Open, Bid, self.volume[symbol], OrderType.Limit)   # # OffsetType.Open   OffsetType.Close   OffsetType.CloseToday  OffsetType.CloseYesterday
        # # # 平多单
        if Position["方向"]=="Long" and dif[-1]<dea[-1] and dif[-2] > dea[-2]:
            self.send(symbol, DirectionType.Sell, OffsetType.Close, Bid, self.volume[symbol], OrderType.Limit)         
        # # # 平空单        
        if Position["方向"]=="Short" and dif[-1]>dea[-1] and dif[-2] < dea[-2]:
            self.send(symbol, DirectionType.Buy, OffsetType.Close, Ask, self.volume[symbol], OrderType.Limit)
if __name__ == '__main__':
    # Config 配置模板
    Config = {'brokerid':'9999', 'userid':'123456', 'password':'******', 'appid':'simnow_client_test', 'auth_code':'0000000000000000', 'product_info':'python dll', 'td_address':'tcp://180.168.146.187:10130', 'md_address':'tcp://180.168.146.187:10131'}
    # Config = {'brokerid':'9999', 'userid':'127922', 'password':'******', 'appid':'simnow_client_test', 'auth_code':'0000000000000000', 'product_info':'python dll', 'td_address':'tcp://180.168.146.187:10101', 'md_address':'tcp://180.168.146.187:10111'} 
    t = CTP(MACDStrategy())
    t.Login(Config)   
    
