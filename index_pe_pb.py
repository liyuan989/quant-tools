# -*- coding: utf-8 -*-

# 运行平台: https://www.joinquant.com/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bisect


#指定日期的指数PE(等权重)(TTM市盈率)
def get_index_pe_date(index_code, date):
    stocks = get_index_stocks(index_code, date)
    q = query(valuation).filter(valuation.code.in_(stocks))
    df = get_fundamentals(q, date)
    if len(df) > 0:
        pe = len(df) / sum([1 / p if p > 0 else 0 for p in df.pe_ratio]) #若需要静态市盈率，则需用pe_ratio_lyr
        return pe
    else:
        return float('NaN')


#指定日期的指数PB（等权重）
def get_index_pb_date(index_code, date):
    stocks = get_index_stocks(index_code, date)
    q = query(valuation).filter(valuation.code.in_(stocks))
    df = get_fundamentals(q, date)
    if len(df) > 0:
        pb = len(df) / sum([1 / p if p > 0 else 0 for p in df.pb_ratio])
        return pb
    else:
        return float('NaN')

    
#指数历史PEPB
def get_index_pe_pb(index_code):
    end = pd.datetime.today()
    first_data = datetime.datetime(year = 2005, month = 1, day = 1)
    start = first_data + datetime.timedelta(days = end.day - 2)
    #start = end - datetime.timedelta(days = 365 * 10 + 1)
    dates = []
    pes = []
    pbs = []
    average_pes = []
    average_pbs = []
    for d in pd.date_range(start, end, freq = 'M'): #频率为月
        pe = get_index_pe_date(index_code, d)
        pb = get_index_pb_date(index_code, d)
        if pe > 0.0 and pb > 0.0:
            pes.append(pe)
            pbs.append(pb)
            average_pes.append(sum(pes) / len(pes))
            average_pbs.append(sum(pbs) / len(pbs))
            dates.append(d)
    d = {
        'PE' : pd.Series(pes, index = dates),
        'PB' : pd.Series(pbs, index = dates),
        'AVERAGE_PE' : pd.Series(average_pes, index = dates),
        'AVERAGE_PB' : pd.Series(average_pbs, index = dates),
    }
    PB_PE = pd.DataFrame(d)
    return PB_PE


all_index = get_all_securities(['index'])

index_choose = [
    #主要宽基指数
    '000001.XSHG', #上证指数
    '399106.XSHE', #深证综指
    '000016.XSHG', #上证50            
    '000300.XSHG', #沪深300
    '000010.XSHG', #上证180
    '000905.XSHG', #中证500
    '399330.XSHE', #深证100
    '399005.XSHE', #中小板指
    '399006.XSHE', #创业板指
    '000015.XSHG', #红利指数
    
    #行业指数
    '000066.XSHG', #上证商品
    '000991.XSHG', #全指医药
    '000933.XSHG', #中证医药
    '000992.XSHG', #全指金融
    '000990.XSHG', #全指消费
    '000932.XSHG', #中证消费
    '000827.XSHG', #中证环保
    '000993.XSHG', #全指信息
    '399812.XSHE', #中证养老产业指数
    '399989.XSHE', #中证医疗
    '399396.XSHE', #国证食品饮料指数
    '000922.XSHG', #中证红利 
    '399967.XSHE', #中证军工
]

df_pe_pb = pd.DataFrame()
frames = pd.DataFrame()
today = pd.datetime.today()

for code in index_choose:
    index_name = all_index.ix[code].display_name  
    print u'正在处理: ', index_name   
    df_pe_pb = get_index_pe_pb(code)        
    results = []

    pe = get_index_pe_date(code, today)
    q_pes = [df_pe_pb['PE'].quantile(i / 10.0) for i in range(11)]    
    index_pe = bisect.bisect(q_pes, pe)
    if index_pe <= 0:
        quantile_pe = 0
    elif index_pe < len(q_pes):
        quantile_pe = index_pe - (q_pes[index_pe] - pe) / (q_pes[index_pe] - q_pes[index_pe - 1])
    else:
        quantile_pe = 10   
    results.append(
        [
            index_name, 
            today.strftime('%Y-%m-%d'), 
            '%.2f' % pe, 
            '%.2f' % df_pe_pb['AVERAGE_PE'][-1], 
            '%.2f' % (quantile_pe * 10)
        ] + 
        ['%.2f' % q for q in q_pes] + [df_pe_pb['PE'].count()]
    )

    pb = get_index_pb_date(code, today)
    q_pbs = [df_pe_pb['PB'].quantile(i / 10.0)  for i in range(11)]
    index_pb = bisect.bisect(q_pbs, pb)
    if index_pb <= 0:
        quantile_pb = 0
    elif index_pb < len(q_pbs):
        quantile_pb = index_pb - (q_pbs[index_pb] - pb) / (q_pbs[index_pb] - q_pbs[index_pb - 1])
    else:
        quantile_pb = 10   
    results.append(
        [
            index_name, 
            today.strftime('%Y-%m-%d'), 
            '%.2f' % pb,
            '%.2f' % df_pe_pb['AVERAGE_PB'][-1],
            '%.2f' % (quantile_pb * 10)
        ] + 
        ['%.2f' % q for q in q_pbs] + [df_pe_pb['PB'].count()]
    )

    df_pe_pb['10% PE'] = q_pes[1]
    df_pe_pb['30% PE'] = q_pes[3]
    df_pe_pb['50% PE'] = q_pes[5]
    df_pe_pb['90% PE'] = q_pes[9]
    df_pe_pb['10% PB'] = q_pbs[1]
    df_pe_pb['30% PB'] = q_pbs[3]
    df_pe_pb['50% PB'] = q_pbs[5]
    df_pe_pb['90% PB'] = q_pbs[9]    
    df_pe_pb.plot(secondary_y = ['AVERAGE_PB', 'PB', '10% PB', '30% PB', '50% PB', '90% PB'],
                  figsize = (18, 10),
                  title = index_name,
                  style = ['m-.', 'm', 'k-.', 'k', 'g', 'c', 'y', 'r', 'g-.', 'c-.', 'y-.', 'r-.'])

    columns = [u'名称', u'当前日期', u'当前估值', u'平均估值', u'分位点%', u'最小估值'] + \
        ['%d%%' % (i * 10) for i in range(1, 10)] + [u'最大估值' , u"数据个数"]
    df = pd.DataFrame(data = results, index = ['PE', 'PB'], columns = columns)
    frames = pd.concat([frames, df])

frames
