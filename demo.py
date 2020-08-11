from 指标库 import *
from Trade import *
import matplotlib.pyplot as plt
def KDJ策略(止损点=None,滑点=None):
    daima= input('请输入合约代码：')
    行情 = Get_kline(daima)
    指标 = TAInstance() # 创建对象

    KDJ = 指标.KDJ(行情) # 取KDJ指标数组
    K = KDJ[0]         # 获取K的值，返回一个数组
    D = KDJ[1]         # 获取D的值，返回一个数组
    J = KDJ[2]         # 获取J的值，返回一个数组
    
    MACD = 指标.MACD(行情) # 取MACD指标数组
    dif = MACD[0]        # 获取dif的值，返回一个数组
    dea = MACD[1]        # 获取dea的值，返回一个数组
    macd = MACD[2]       # 获取macd的值，返回一个数组
    账户权益 = []
    收盘价 = []
    close,High,low = 指标.tick(行情)      # 取收盘价数组 # 获取最新价格（卖价），用于开平仓
    print(len(close))
    for i in range(50,len(K)):  #50开始测试因为技术指标值有时为空值
        持仓 = GetPosition(daima)    #查持仓
        账户权益.append(round(GetAccount()["账户权益"],2))
        收盘价.append(round(close[i],2))
        print(GetAccount())    #查可用资金
        print(持仓)           #显示持仓
        # 开多单
        if 持仓["手数"] == 0 and K[i]>30 and K[i-1]<30 and dea[i]>0:
            最小值 = min(low[i-9:i])
            # if 最小值 == low[i]:
                # 最小值 = low[i]-1
            # print(最小值)
            # if daima[0] in ['0', '3', '6']:
                # 手数 =int((GetAccount()["账户权益"]*0.01)/(close[i]-最小值)/100)
            # else:
                # 手数 =int((GetAccount()["账户权益"]*0.01)/(close[i]-最小值))
            # if 手数 < 0:
                # 手数 = 1
            手数 = 1
            Buy(daima, close[i]+滑点, 手数,最小值,close[i]+(close[i]-最小值)*3)      # 合约, 方向, 价格, 手数, 止损=None, 止盈=None
        
        # 开空单
        if 持仓["手数"] == 0 and K[i]<70 and K[i-1]>70 and dea[i]<0:
            最大值 = max(High[i-9:i])
            # if 最大值 == High[i]:
                # 最大值 = High[i]+1
            # print(最大值)
            # if daima[0] in ['0', '3', '6']:
                # 手数 =int((GetAccount()["账户权益"]*0.01)/(最大值-close[i])/100)
            # else:
                # 手数 =int((GetAccount()["账户权益"]*0.01)/(最大值-close[i]))
            # if 手数 < 0:
                # 手数 = 1
            手数 = 1
            Short(daima, close[i]-滑点,手数,最大值,close[i]-(最大值-close[i])*3)   # 合约, 方向, 价格, 手数, 止损=None, 止盈=None
        
        # 平多单
        if 持仓["方向"] == "BUY" and 持仓["手数"] > 0 and close[i]>持仓["止盈"] or 持仓["方向"] == "BUY" and 持仓["手数"] > 0 and close[i]<持仓["止损"] or 持仓["方向"] == "BUY" and 持仓["手数"] > 0 and dea[i]<0 and dea[i-1]>0:
            Sell(持仓["合约"],close[i]-滑点, 持仓["手数"])     # 合约, 价格, 手数
        
        # 平空单
        if 持仓["方向"] == "Sell" and 持仓["手数"] > 0 and close[i]<持仓["止盈"] or 持仓["方向"] == "Sell" and 持仓["手数"] > 0 and close[i]>持仓["止损"] or 持仓["方向"] == "Sell" and 持仓["手数"] > 0 and dea[i]>0 and dea[i-1]<0:
            Cover(持仓["合约"],close[i]+滑点, 持仓["手数"])    # 合约, 价格, 手数
    print("    ")
    统计()
    #print(账户权益)
    plt.plot(账户权益)
    plt.show()
    plt.plot(收盘价)
    plt.show()
if __name__ == '__main__':
    while True:
        KDJ策略(0,0)
        # daima= input('请输入合约代码：')
        # 行情 = Get_kline(daima,"5m")
        # print(行情)
        # 指标 = TAInstance() # 创建对象
        # KDJ=指标.KDJ(行情)
        # print(KDJ)
        # 通道=指标.通道(行情) # 取通道指标数组
        # print(通道[0])
        # print("K",KDJ[0][-1])
        # print("D",KDJ[1][-1])
        # print("J",KDJ[2][-1])
        """
        低=指标.Lowest(行情,5,"Low") # 5日最低价
        print(低)
        高=指标.Highest(行情,5,"High") # 5日最低价
        print(高)
        通道=指标.通道(行情) # 取通道指标数组
        print(通道)
        tick=指标.tick(行情) # 取收盘价数组
        print(len(tick))
        MA=指标.RSI(行情) # 取MA指标数组
        print(MA)
        EMA=指标.EMA(行情) # 取EMA指标数组
        print(EMA)
        MACD=指标.MACD(行情) # 取MACD指标数组
        print(MACD[1])
        BOLL=指标.BOLL(行情) # 取BOLL指标数组
        print(BOLL)
        KDJ=指标.KDJ(行情) #  取KDJ指标数组
        print(KDJ)
        RSI=指标.RSI(行情) # 取RSI指标数组
        print(RSI)
        ATR=指标.ATR(行情) #  取ATR指标数组
        print(ATR)"""
