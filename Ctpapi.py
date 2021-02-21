
import thosttraderapi as tdapi
import thostmduserapi as mdapi
import pandas as pd
from datetime import datetime
import time
import os, os.path
import random
import json
from urllib import request
import threading
from ta import *
class BarType():
    """时间类型:秒,分,时,日,周,月,年"""
    """3秒"""
    Time3 = 3
    '''5秒'''
    Time5 = 5
    '''15秒'''
    Time15 = 15
    '''30秒'''
    Time30 = 30
    '''1分钟'''
    Min = 60
    '''3分钟'''
    Min3 = 180
    '''5分钟'''
    Min5 = 300
    '''15分钟'''
    Min15 = 900
    '''30分钟'''
    Min30 = 1800
    '''60分钟'''
    Min60 = 3600
    '''日'''
    Day = 14000
    '''周'''
    Week = 4
    '''月'''
    Month = 5
    '''年'''
    Year = 6
 
 
    def __int__(self):
        """return int value"""
        return self.value        
class OrderType():
    """委托类型"""
    Limit = "0"
    '''限价单'''
    Market = "1"
    '''市价单'''
    FAK = "2"
    '''部成立撤'''
    FOK = "3"
    '''全成立撤'''

    def __int__(self):
        return self.value
class OffsetType():
    """开平标志类型"""
    Open = "0"
    """开仓"""
    Close = "1"
    """平仓"""
    CloseToday = "3"
    """平今"""
    CloseYesterday = "4"
    """平昨"""
    def __int__(self):
        return self.value    
class DirectionType():
    """买卖方向类型"""
    Buy = "0"
    """买"""
    Sell = "1"
    def __int__(self):
        return self.value


class TdSpi(tdapi.CThostFtdcTraderSpi):
    # 继承重写c++的tdapi方法，交易连接
    def __init__(self, setting, BaseGateway):
        tdapi.CThostFtdcTraderSpi.__init__(self)
        self.userid = setting["userid"]
        self.password = setting["password"]
        self.brokerid = setting["brokerid"]
        self.td_address = setting["td_address"]
        self.md_address = setting["md_address"]
        self.appid = setting["appid"]
        self.auth_code = setting["auth_code"]
        self.product_info = setting["product_info"]
        self.Gateway = BaseGateway
        self.reqID = 0              # 操作请求编号
        self.OrderRefID = random.randrange(start=1000,stop=9000,step=random.randint(10,100)  )           # 订单编号
        self.login = False
        self.lock = False # 锁机制，用于确保系统前后操作，下单超过1秒废单
        self.position = None
        self.positionCache = {}
        self.account = {}
        self.contract = {}
        self.api = self.create()
        self.connect()
    def create(self):
        tradepath = os.getcwd() + '/' + self.userid + '/trade/' #LOGS_DIR +"md"
        if not os.path.exists(tradepath):
            os.makedirs(tradepath)
        return tdapi.CThostFtdcTraderApi_CreateFtdcTraderApi(tradepath)
    def OnFrontConnected(self):
        obj = tdapi.CThostFtdcReqAuthenticateField()
        obj.BrokerID = self.brokerid
        obj.UserID = self.userid
        obj.AppID = self.appid
        obj.AuthCode = self.auth_code
        self.api.ReqAuthenticate(obj, 0)

    def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        if not pRspInfo.ErrorID :
            obj = tdapi.CThostFtdcReqUserLoginField()
            obj.BrokerID = self.brokerid
            obj.UserID = self.userid
            obj.Password = self.password
            obj.UserProductInfo = "python dll"
            self.api.ReqUserLogin(obj, 0)
        else:
            print('认证错误 {}'.format(pRspInfo.ErrorMsg))

    def OnFrontDisconnected(self, nReason: 'int'):
        # 服务器断开
        print('交易服务器断开 !')
        self.login = False

    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 账户登录
        if not pRspInfo.ErrorID:
            print('用户登录')
            obj = tdapi.CThostFtdcQrySettlementInfoField()
            obj.BrokerID = self.brokerid
            obj.InvestorID = self.userid
            obj.TradingDay = pRspUserLogin.TradingDay
            self.api.ReqQrySettlementInfo(obj, 0)
        else:
            print('登录错误 {}'.format(pRspInfo.ErrorMsg))

    def OnRspQrySettlementInfo(self, pSettlementInfo: 'CThostFtdcSettlementInfoField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 结算确认
        if pSettlementInfo is not None :
            print('content {}'.format(pSettlementInfo.Content))
        if bIsLast :
            obj = tdapi.CThostFtdcSettlementInfoConfirmField()
            obj.BrokerID = self.brokerid
            obj.InvestorID = self.userid
            self.api.ReqSettlementInfoConfirm(obj, 0)
            print('结算确认')
            # print(pSettlementInfo.Content)

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: 'CThostFtdcSettlementInfoConfirmField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 获取交易结算信息Content
        if not pRspInfo.ErrorID:
            self.login = True
            self.qryInstrument()
        else:
            print('结算错误 {}'.format(pRspInfo.ErrorMsg))

    def OnRtnOrder(self, pOrder: 'CThostFtdcOrderField'):
        # 需要根据报单确定是否成交，未成交需要通知交易系统进行处理，需要维护报单列表
        print('OrderStatus={}, StatusMsg={}, LimitPrice={}'.format(pOrder.OrderStatus, pOrder.StatusMsg, pOrder.LimitPrice))

    def OnRtnTrade(self, pTrade: 'CThostFtdcTradeField'):
        # 由于交易所返回持仓有延迟，所以需要自己维护持仓列表或者在交易系统根据成交回报维护持仓列表
        # ExchangeID 交易所代码
        # TradeID 成交编号
        # Direction 买卖方向
        # OrderRef 报单引用
        # OrderSysID 报单编号
        # TraderID 交易所交易员代码
        # OrderLocalID 本地报单编号
        # InstrumentID 合约代码
        # OffsetFlag 开平标志
        # Price 价格
        # Volume 数量
        exchangeID = pTrade.ExchangeID
        tradeID = pTrade.TradeID
        side = 'Long' if pTrade.Direction=='0' else 'Short' # 0 多 1 空
        orderRef = pTrade.OrderRef
        orderSysID = pTrade.OrderSysID
        traderID = pTrade.TraderID
        orderLocalID = pTrade.OrderLocalID
        code = pTrade.InstrumentID
        offsetFlag = 'Buy' if pTrade.OffsetFlag=='0' else 'Sell' # 0 买 1 卖
        price = pTrade.Price
        amount = pTrade.Volume
        if pTrade.Direction == '0' and pTrade.OffsetFlag == '0':			
            offset = "买开"
            # side = "Buy"
        elif pTrade.Direction == '1' and pTrade.OffsetFlag =='3' or pTrade.Direction == '1' and pTrade.OffsetFlag == '4' or pTrade.Direction == '1' and pTrade.OffsetFlag == '1':
            offset = "买平"
            # side = "Sell"
        elif pTrade.Direction == '1' and pTrade.OffsetFlag == '0':
            offset = "卖开"
            # side = "Short"
        elif pTrade.Direction == '0' and pTrade.OffsetFlag == '3' or pTrade.Direction == '0' and pTrade.OffsetFlag == '4' or pTrade.Direction == '0' and pTrade.OffsetFlag == '1':
            offset = "卖平"
            # side = "Cover"
        LL ={'symbol':code,'volume':amount,'price':price,'Direction':side,'offset':offset}
        # print(LL)
        self.Gateway.on_trade({"合约":code,"盈亏":0,"持仓成本":0,"今仓":0,"昨仓":0,"方向":offset,"开仓价":price,"总持仓":amount,"止损":0,"止盈":0,"移动止损":0})
        self.Gateway.position = []
        self.qryPosition()

    def OnRspOrderInsert(self, pInputOrder: 'CThostFtdcInputOrderField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 订单反馈
        if pRspInfo.ErrorID:
            print('订单错误 {} {}'.format(pRspInfo.ErrorID, pRspInfo.ErrorMsg))	

    def OnRspQryInvestorPosition(self, pInvestorPosition: 'CThostFtdcInvestorPositionField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # InstrumentID 合约代码
        # BrokerID 经纪公司代码
        # InvestorID 投资者代码
        # PosiDirection 持仓多空方向，'2'表示多头持仓，'3'表示空头持仓
        # HedgeFlag 投机套保标志
        # PositionDate 持仓日期，区分是否历史仓的枚举值，1表示当前交易日持仓，2表示是历史仓（昨仓）
        # YdPosition 上日持仓
        # Position 总持仓
        # TodayPosition 今日持仓
        # LongFrozen 多头冻结
        # ShortFrozen 空头冻结
        # OpenVolume 开仓量，当天该键值上总的开仓量  
        # CloseVolume 平仓量, 当天该键值上总的平仓量   
        # PositionCost 持仓成本, 当天新开仓按开仓价计算，昨仓则是用昨结算价计算，计算公式为price*volume*RateMultiple    
        # OpenCost 开仓成本, 新老仓都是按照开仓价计算的成本，如果无昨仓与持仓成本字段是相同的值
        # CloseProfit 平仓盈亏, 等于下面的逐日盯市平仓盈亏 
        # PositionProfit 持仓盈亏, 按最新价计算出来的持仓值与持仓成本的差值
        # CloseProfitByDate 逐日盯市平仓盈亏,  昨仓是平仓价与昨结算价计算出的盈亏，今仓是平仓价与开仓价计算出的盈亏 ，计算公式为（closeprice - openprice或preSettlementPrice）*volume*RateMultiple 
        # CloseProfitByTrade 逐笔对冲平仓盈亏, 平仓价与开仓价计算出的盈亏 
        # MarginRateByMoney 保证金率,  该合约的交易保证金率，同查询所得值一致。昨仓无此值
        # MarginRateByVolume 保证金率(按手数), 该合约的交易保证金率(按手数)，同查询所得值一致。昨仓无此值
        code = pInvestorPosition.InstrumentID
        amount = pInvestorPosition.Position
        td_amount = pInvestorPosition.TodayPosition
        side = 'Long' if pInvestorPosition.PosiDirection=='2' else 'Short'
        cost = pInvestorPosition.PositionCost
        profit = pInvestorPosition.PositionProfit
        key = code+side
        # 上期所持仓的今昨分条返回(有昨仓、无今仓)
        if amount>0:
            if key in self.positionCache:
                self.positionCache[key]['总持仓'] += amount
                self.positionCache[key]['今仓'] += td_amount
                self.positionCache[key]['持仓成本'] += cost
                self.positionCache[key]['盈亏'] += profit
                # 其它交易所统一返回
            else:
                self.positionCache[key] = {'合约':code,'总持仓':amount,'今仓':td_amount,'方向':side,'持仓成本':cost,'盈亏':profit}

        if bIsLast:
            if self.positionCache:
                self.position = pd.DataFrame(self.positionCache.values())
                self.position = self.position.set_index('合约')
                self.position['size'] = self.contract.loc[self.position.index, 'size']
                self.position['开仓价'] = self.position['持仓成本']/(self.position['size']*self.position['总持仓'])
                self.position['昨仓'] = self.position['总持仓']-self.position['今仓']
                self.position['合约'] = self.position.index
                position=self.position.to_dict(orient='records')
                self.Gateway.position = position
                self.positionCache.clear()
                print(self.position)
                self.position = None
                # print(self.Gateway.position)
            else:
                print("没有持仓")
                # self.Gateway.position = []

    def OnRspQryTradingAccount(self, pTradingAccount: 'CThostFtdcTradingAccountField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 账户查询反馈
        self.account['balance'] = pTradingAccount.Balance
        self.account['available'] = pTradingAccount.Available
        self.account['commission'] = pTradingAccount.Commission
        self.account['margin'] = pTradingAccount.CurrMargin
        self.account['closeProfit'] = pTradingAccount.CloseProfit
        self.account['positionProfit'] = pTradingAccount.PositionProfit
        print(self.account)
    def OnRspQryInstrument(self, pInstrumentMarginRate: 'CThostFtdcInstrumentMarginRateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        # 合约查询反馈
        code = pInstrumentMarginRate.InstrumentID
        exchange = pInstrumentMarginRate.ExchangeID
        name = pInstrumentMarginRate.InstrumentName
        size = pInstrumentMarginRate.VolumeMultiple
        priceTick = pInstrumentMarginRate.PriceTick
        strikePrice = pInstrumentMarginRate.StrikePrice
        productClass = pInstrumentMarginRate.ProductClass
        expiryDate = pInstrumentMarginRate.ExpireDate
        optionsType = pInstrumentMarginRate.OptionsType
        self.contract[code] = {'code':code, 'exchange':exchange, 'name':name, 'size':size, 'priceTick':priceTick, 'strikePrice':strikePrice,'productClass':productClass, 'expiryDate':expiryDate, 'optionsType':optionsType}
        if bIsLast:
            self.contract = pd.DataFrame(self.contract.values())
            self.contract = self.contract.set_index('code')
            print(self.contract)
            self.lock = False
            self.qryPosition()
    def connect(self):
        # 连接
        self.api.RegisterFront(self.td_address)
        self.api.RegisterSpi(self)
        self.api.SubscribePrivateTopic(tdapi.THOST_TERT_QUICK)
        self.api.SubscribePublicTopic(tdapi.THOST_TERT_QUICK)				
        self.api.Init()
        self.Gateway.setTraderSpi(self)

    def send(self, symbol, Direction, Offset, Price, volume, PriceType):
        # 下单，简单化处理
        if self.lock==True:
            time.sleep(0.1)
        self.reqID += 1
        self.OrderRefID += 1
        obj = tdapi.CThostFtdcInputOrderField()
        obj.BrokerID = self.brokerid  # 经纪公司代码
        obj.ExchangeID = self.contract.loc[symbol,'exchange'] # 交易所代码[orderReq.symbol]  # 交易所代码 
        obj.InstrumentID = symbol    # 合约代码
        obj.UserID = self.userid  # 投资者代码
        obj.InvestorID = self.userid  # 投资者代码
        obj.Direction = Direction # 买卖方向 '0' #买'1' #卖
        obj.LimitPrice = Price     # 价格
        obj.VolumeTotalOriginal = volume   # 数量
        obj.OrderPriceType = PriceType   #tdapi.THOST_FTDC_OPT_LimitPrice # 报单价格条件'1' #任意价'2' #限价'3' #最优价'4' #最新价'8' #卖一价'C' #买一价
        obj.ContingentCondition = tdapi.THOST_FTDC_CC_Immediately  # 触发条件'1' #立即'2' #止损'3' #止赢'4' #预埋单
        obj.TimeCondition = tdapi.THOST_FTDC_TC_GFD      # 有效期类型 '1' #立即完成，否则撤销'2' #本节有效'3' #当日有效'4' #指定日期前有效'5' #撤销前有效'6' #集合竞价有效
        obj.VolumeCondition = tdapi.THOST_FTDC_VC_AV     # 成交量类型'1' #任何数量'2' #最小数量'3' #全部数量
        obj.CombHedgeFlag ="1"   # 组合投机套保标志'1' #投机'2' #套利'3' #套保
        obj.CombOffsetFlag = Offset  # 组合开平标志'0' #开仓'1' #平仓'3' #平今'4' #平昨
        obj.GTDDate = ""
        obj.orderfieldRef = str(self.OrderRefID) # 报单引用
        obj.MinVolume = 0  # 最小成交量
        obj.ForceCloseReason = tdapi.THOST_FTDC_FCC_NotForceClose  # 强平原因 '0' #非强平'1' #资金不足'2' #客户超仓
        obj.IsAutoSuspend = 0  # 自动挂起标志
        if obj.OrderPriceType == OrderType.Market:  # 市价
            obj.OrderPriceType = tdapi.THOST_FTDC_OPT_AnyPrice   #  """任意价"""
            obj.TimeCondition = tdapi.THOST_FTDC_TC_IOC         #  """立即完成，否则撤销"""
            obj.LimitPrice = 0.0
            obj.VolumeCondition = tdapi.THOST_FTDC_VC_AV   #  """任何数量"""
        elif obj.OrderPriceType == OrderType.Limit:  # 限价
            obj.OrderPriceType = tdapi.THOST_FTDC_OPT_LimitPrice # """限价"""
            obj.TimeCondition = tdapi.THOST_FTDC_TC_GFD  # """当日有效"""
            obj.LimitPrice = Price
            obj.VolumeCondition = tdapi.THOST_FTDC_VC_AV #  """任何数量"""
        elif obj.OrderPriceType == OrderType.FAK:  # FAK
            obj.OrderPriceType = tdapi.THOST_FTDC_OPT_LimitPrice #   """限价"""
            obj.TimeCondition = tdapi.THOST_FTDC_TC_IOC #   """立即完成，否则撤销"""
            obj.LimitPrice = Price
            obj.VolumeCondition = tdapi.THOST_FTDC_VC_AV #   """任何数量"""       
        elif obj.OrderPriceType == OrderType.FOK:  # FOK
            obj.OrderPriceType = tdapi.THOST_FTDC_OPT_LimitPrice # """限价"""
            obj.TimeCondition = tdapi.THOST_FTDC_TC_IOC #  """立即完成，否则撤销"""
            obj.LimitPrice = Price
            obj.VolumeCondition = tdapi.THOST_FTDC_VC_CV  # 全部数量
        self.api.ReqOrderInsert(obj,self.reqID)
        self.lock==True	  
        return str(self.OrderRefID) # 报单编号
    def qryInstrument(self):
        # 查询合约
        if len(self.contract)==0:
            obj = tdapi.CThostFtdcQryInstrumentField()
            self.api.ReqQryInstrument(obj, 0)
            self.lock = True
    def qryPosition(self):
        # 查询持仓
        while self.lock==True:
            time.sleep(0.1)
        obj = tdapi.CThostFtdcQryInvestorPositionField()
        self.api.ReqQryInvestorPosition(obj, 0)
    def qryAccount(self):
        # 查询账户
        while self.lock==True:
            time.sleep(0.1)
        obj = tdapi.CThostFtdcQryTradingAccountField()
        self.api.ReqQryTradingAccount(obj, 0)
    def __del__(self):
        self.api.RegisterSpi(None)
        self.api.Release()



class MdSpi(mdapi.CThostFtdcMdSpi):

    def __init__(self,setting,BaseGateway):
        mdapi.CThostFtdcMdSpi.__init__(self)
        # super().__init__()
        self.userid = setting["userid"]
        self.password = setting["password"]
        self.brokerid = setting["brokerid"]
        self.td_address = setting["td_address"]
        self.md_address = setting["md_address"]
        self.appid = setting["appid"]
        self.auth_code = setting["auth_code"]
        self.product_info = setting["product_info"]
        self.reqid = 0
        self.Gateway = BaseGateway
        self.nest = {}
        self.api = self.create()
        self.connect()
    def create(self):
        mdpath = os.getcwd() + '/' + self.userid + '/md/' #LOGS_DIR +"md"
        if not os.path.exists(mdpath):
            os.makedirs(mdpath)
        return mdapi.CThostFtdcMdApi_CreateFtdcMdApi(mdpath)
    def Bar(self, tick, granularity = 30):
        instrument_id = tick.InstrumentID
        action_day = tick.ActionDay
        update_time = tick.UpdateTime.replace(':', '')
     
        last_price = tick.LastPrice
     
        volume = tick.Volume
     
        if update_time.find('.') != -1:
            dt = datetime.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S.%f")
            timestamp = time.mktime(dt.timetuple()) + (dt.microsecond / 1e6)
     
        else:
            timestamp = int(time.mktime(time.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S")))
     
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        remainder = timestamp % granularity

        if instrument_id not in self.nest:
            self.nest[instrument_id] = {
                'Date': date_time,
                'Open': last_price,
                'High': last_price,
                'Low': last_price,
                'Close': last_price,
                'Volume': volume,
                'last_time': timestamp,
            }
        else:
            if remainder == 0 or (timestamp - self.nest[instrument_id]['last_time'])>= granularity:
                self.nest[instrument_id]['Volume'] = volume - self.nest[instrument_id]['Volume']
                self.nest[instrument_id]['Date'] = date_time
                # print(instrument_id,self.nest[instrument_id])
                # self.Gateway.SetData(instrument_id,self.nest[instrument_id])
                # self.Gateway.on_bar(tick,self.nest[instrument_id])
                self.Gateway.on_bar(tick,self.Gateway.SetData(instrument_id,self.nest[instrument_id]))
                del self.nest[instrument_id]
            else:
                self.nest[instrument_id]['Date'] = date_time     
                self.nest[instrument_id]['Close'] = last_price
                if last_price > self.nest[instrument_id]['High']:
                    self.nest[instrument_id]['High'] = last_price
             
                elif last_price < self.nest[instrument_id]['Low']:
                    self.nest[instrument_id]['Low'] = last_price
    def OnFrontConnected(self) -> "void":
        print ("行情初始化")
        self.login()
    def login(self):
        req = mdapi.CThostFtdcReqUserLoginField()
        req.BrokerID = self.brokerid   # 经纪公司代码
        req.UserID = self.userid       # 投资者代码
        req.Password = self.password       # 投资者代码
        req.UserProductInfo = self.product_info
        self.reqid += 1
        self.api.ReqUserLogin(req,self.reqid)
    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        print (f"OnRspUserLogin, SessionID={pRspUserLogin.SessionID},ErrorID={pRspInfo.ErrorID},ErrorMsg={pRspInfo.ErrorMsg}")
        self.api.SubscribeMarketData([id.encode('utf-8') for id in self.Gateway.symbol_lsit],len(self.Gateway.symbol_lsit))
    def OnRtnDepthMarketData(self, pDepthMarketData: 'CThostFtdcDepthMarketDataField') -> "void":
        # threading.Thread(target=self.Bar, args=(pDepthMarketData,self.Gateway.BarType)).start()
        self.Bar(pDepthMarketData,self.Gateway.BarType)
        self.Gateway.on_tick(pDepthMarketData)
        
    def OnRspSubMarketData(self, pSpecificInstrument: 'CThostFtdcSpecificInstrumentField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool'):
        print ("订阅 合约")
        print ("InstrumentID=",pSpecificInstrument.InstrumentID)
        # print ("ErrorID=",pRspInfo.ErrorID)
        # print ("ErrorMsg=",pRspInfo.ErrorMsg)
    def connect(self):
        self.api.RegisterFront(self.md_address)
        self.api.RegisterSpi(self)
        self.Gateway.setMDSpi(self)
        self.api.Init()      
        self.api.Join()
    def __del__(self):
        self.api.RegisterSpi(None)
        self.api.Release()
    def SubMarketData(self, symbol):
        Req = self.api.SubscribeMarketData([id.encode('utf-8') for id in symbol],len(symbol))
        return Req

# class Strategy(TAInstance):
class Strategy():
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["ni2109","sc2109","ag2109"]  #订阅合约
        self.BarType = BarType.Min  #订阅K线周期  秒级 BarType.Time3  Time5  Time15  Time30       分钟级  BarType.Min、  Min3 、 Min5 、 Min15 、 Min30 、 Min60
        self.data = []
        self.position = []
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
    def GetPosition(self, symbol=None):
        for i in self.position:
            if symbol==i['合约']:
                return i
                break
        else:
            # print('该合约没有持仓')
            Position = {"合约":0,"盈亏":0,"持仓成本":0,"总持仓":0,"今仓":0,"昨仓":0,"方向":"None","开仓价":0}
            return Position
    def GetData(self, symbol=None):
        for i in self.data:
            if symbol==i[0]["symbol"]:
                return i
                # break
        else:
             print('该合约没有数据')
             return None
    def SetData(self, symbol=None,Bar=None):
        for i in self.data:
            if symbol==i[0]["symbol"]:
                i[-1]["data"].append(Bar)
                return i
                break
        else:
             print('该合约没有数据')
             new_Data = []
             new_Bar = []
             new_Bar.append(Bar)
         
             new_ohlcv = {}
             new_ohlcv['symbol'] = symbol
             new_ohlcv['data'] = new_Bar
             new_Data.append(new_ohlcv)
             self.data.append(new_Data)
             return new_Data            
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
