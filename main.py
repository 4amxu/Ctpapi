from Ctpapi import *

class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["ni2103","rb2105","ag2102"]  #订阅合约
        self.bar_time = 5  #K线周期以秒计
        self.volume = 1  #下单手数
    def on_tick(self, tick=None):
        print(tick.LastPrice)  
    def on_bar(self, tick=None, bar=None):
        symbol = tick.InstrumentID   #合约代码
        Bid = tick.BidPrice1    #买价
        Ask = tick.AskPrice1    #卖价
        LastPrice = tick.LastPrice  #最新价
        print(symbol)
        print(bar)
        行情 = self.Get_data(symbol)[0]["data"]
        if len(行情) <= 35:   # 小于35 条 退出 
            return                    # 退出 
        # 指标 = TAInstance()             # 创建 指标库 对象
        # # K,D,J  = 指标.KDJ(行情) # 取KDJ指标数组
        dif,dea,macd  = self.MACD(行情) # 取MACD指标数组

        close,High,low = self.tick(行情)      # 取收盘价数组 # 获取最新价格（卖价）
        print("K线收盘价",close[-1])     # 取最新K线 收盘价
        print("dif",dif[-10:])        # 显示10个 dif 元素
        print("dea",dea[-10:])         # 显示10个 dea 元素
        print("macd",macd[-10:])        # 显示10个 macd 元素
        Posion = self.GetPosition(symbol)   # 通过  GetPosition() 函数 查询持仓情况
        print(Posion)    
        # 开多单
        if Posion["手数"] == 0 and dif[-1]>0 and dif[-2]<0 or Posion["手数"] == 0 and dif[-1]>dea[-1] and dif[-2] < dea[-2] and dea[-1] > 0:
            print("MACD策略开多Buy")
            最低价 = min(low[-10:])
            最高价 = max(High[-10:])
            self.Buy(symbol, Ask, self.volume, 最低价, Ask+(Ask-最低价)*3)      # 合约, 价格, 手数, 止损=None, 止盈=None   本地设置 止损 止盈 等用函数           
        # # 开空单
        if Posion["手数"] == 0 and dif[-1]<0 and dif[-2]>0 or Posion["手数"] == 0 and dif[-1]<dea[-1] and dif[-2] > dea[-2] and dea[-1] < 0:
            print("MACD策略开空Short")
            最低价 = min(low[-10:])
            最高价 = max(High[-10:])
            self.Short(symbol, Bid, self.volume, 最高价, Bid-(最高价-Bid)*3)   # 合约, 价格, 手数, 止损=None, 止盈=None   本地设置 止损 止盈 等用函数        
        # # 平多单
        if Posion["方向"]=='Buy' and LastPrice < Posion["止损"] and Posion["止损"] != 0 or Posion["方向"]=='Buy' and LastPrice > Posion["止盈"] and Posion["止盈"] != 0 or Posion["方向"]=='Buy' and LastPrice > Posion["价格"] and dif[-1]<dea[-1] and dif[-2] > dea[-2]:   #Posion["方向"]=='Buy' and dif[-1]<dea[-1] and dif[-2] > dea[-2]
            print("MACD策略平多Sell")
            self.Sell(symbol,Bid, Posion["手数"])     # 合约, 价格, 手数        
        # # 平空单
        if Posion["方向"]=='Sell' and LastPrice > Posion["止损"] and Posion["止损"] != 0 or Posion["方向"]=='Sell' and LastPrice < Posion["止盈"] and Posion["止盈"] != 0 or Posion["方向"]=='Sell' and LastPrice < Posion["价格"] and dif[-1]>dea[-1] and dif[-2] < dea[-2]: #Posion["方向"]=='Sell' and dif[-1]>dea[-1] and dif[-2] < dea[-2] 
            print("MACD策略平空Cover")
            self.Cover(symbol,Ask, Posion["手数"])    # 合约, 价格, 手数

if __name__ == '__main__':
    配置 = {'经纪商代码':'9999', '用户名':'123456', '密码':'******', '产品名称':'simnow_client_test', '授权编码':'0000000000000000', '产品信息':'python dll', '交易服务器':'tcp://180.168.146.187:10130', '行情服务器':'tcp://180.168.146.187:10131'}
    # 配置 = {'经纪商代码':'9999', '用户名':'23456', '密码':'******', '产品名称':'simnow_client_test', '授权编码':'0000000000000000', '产品信息':'python dll', '交易服务器':'tcp://180.168.146.187:10101', '行情服务器':'tcp://180.168.146.187:10111'}
    登陆 = CTP(MACDStrategy())
    登陆.Login(配置)
    
    
