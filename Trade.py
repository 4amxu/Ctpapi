Account = {"账户权益":1000000,"可用资金":1000000,"占用资金":0,"平仓盈亏":0}
初始资金 = Account["账户权益"]
Position = {"合约":0,"方向":0,"价格":0,"手数":0,"止损":0,"止盈":0}
损益表 = []
手续费 = []
Pos = []
def GetAccount():
    return Account

def GetPosition(合约=None):
    global Account ,Position,Pos
    for i in Pos:
        if 合约==i['合约']:
            #Position.remove(i)
            return i
            break
    else:
         print('该合约没有持仓')
         Position = {"合约":0,"方向":0,"价格":0,"手数":0,"止损":0,"止盈":0}
         return Position
def Buy(合约, 价格, 手数, 止损=None,止盈=None):
    global Account ,Position,Pos
    for i in Pos:
        if 合约==i['合约'] and 方向==i['方向']:
            开仓 = {}
            开仓["合约"]=合约
            开仓["方向"]="BUY"
            开仓["价格"]= (价格 + i['价格'])/2
            开仓["手数"]= 手数 + i['手数']
            开仓["止损"]=止损
            开仓["止盈"]=止盈
            Pos.remove(i)
            Pos.append(开仓)
            Account["占用资金"] = round(价格*手数,2)
            Account["可用资金"] - round(价格*手数,2)
            print("buy  :{}".format(价格))
            break
    else:
         print('开仓')
         开仓 = {}
         开仓["合约"]=合约
         开仓["方向"]="BUY"
         开仓["价格"]=价格
         开仓["手数"]=手数
         开仓["止损"]=止损
         开仓["止盈"]=止盈
         Pos.append(开仓)
         Account["占用资金"] = round(价格*手数,2)
         Account["可用资金"] - round(价格*手数,2)
         print("buy  :{}".format(价格))
def Short(合约, 价格, 手数, 止损=None,止盈=None):
    global Account ,Position,Pos
    for i in Pos:
        if 合约==i['合约'] and 方向==i['方向']:
            开仓 = {}
            开仓["合约"]=合约
            开仓["方向"]="Sell"
            开仓["价格"]= (价格 + i['价格'])/2
            开仓["手数"]= 手数 + i['手数']
            开仓["止损"]=止损
            开仓["止盈"]=止盈
            Pos.remove(i)
            Pos.append(开仓)
            Account["占用资金"] = round(价格*手数,2)
            Account["可用资金"] - round(价格*手数,2)
            print("sell  :{}".format(价格))
            break
    else:
         print('开仓')
         开仓 = {}
         开仓["合约"]=合约
         开仓["方向"]="Sell"
         开仓["价格"]=价格
         开仓["手数"]=手数
         开仓["止损"]=止损
         开仓["止盈"]=止盈
         Pos.append(开仓)
         Account["占用资金"] = round(价格*手数,2)
         Account["可用资金"] - round(价格*手数,2)
         print("sell  :{}".format(价格))
def Sell(合约=None,价格=None, 手数=None):
    global Account ,损益表,手续费
    global Account ,Position,Pos
    for i in Pos:
        if 合约==i['合约'] and i['方向']=="BUY":
            if 价格 < i["止损"] and i["止损"] != 0:
                价格 = i["止损"]
            else:
                价格 = 价格
            
            yingkui=(价格-i["价格"])*手数
            损益表.append(round(yingkui,2))
            手续费.append(round(手数*20,2))
            Account["账户权益"] += round(yingkui,2)
            Account["占用资金"] = 0
            Account["可用资金"] = Account["账户权益"]
            print('平 buy        :{0}   盈亏： {1}'.format(价格,yingkui))
            print("  ")   
            Pos.remove(i)
            break
    else:
        print("平仓错误没有持仓")
        
        
def Cover(合约=None,价格=None, 手数=None):
    global Account ,损益表,手续费
    global Account ,Position,Pos
    for i in Pos:
        if 合约==i['合约'] and i['方向']=="Sell":
            if 价格 > i["止损"] and i["止损"] != 0:
                价格 = i["止损"]
            else:
                价格 = 价格
            
            yingkui=(i["价格"]-价格)*手数
            损益表.append(round(yingkui,2))
            手续费.append(round(手数*20,2))
            Account["账户权益"] += round(yingkui,2)
            Account["占用资金"] = 0
            Account["可用资金"] = Account["账户权益"]
            print('平 Sell        :{0}   盈亏： {1}'.format(价格,yingkui))
            print("  ")   
            Pos.remove(i)
            break
    else:
        print("平仓错误没有持仓")

