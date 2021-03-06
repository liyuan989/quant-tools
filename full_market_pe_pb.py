# -*- coding: utf-8 -*-

# 运行平台: https://www.joinquant.com/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bisect

index_code = [
    '000001.XSHG', #上证指数
    '399106.XSHE', #深证综指
]


#指定日期的指数PE(等权重)(TTM市盈率)
def get_index_pe_date(date):
    #stocks = get_index_stocks(index_code, date)
    total_count = 0
    total_pe_sum = 0.0
    for code in index_code:
        stocks = get_index_stocks(code, date)
        q = query(valuation).filter(valuation.code.in_(stocks))
        df = get_fundamentals(q, date)
        if len(df) > 0:
            total_count += len(df)
            total_pe_sum += sum([1 / p if p > 0 else 0 for p in df.pe_ratio])
        else:
            total_count += float('NaN')
    if total_pe_sum > 0:
        return total_count / total_pe_sum
    else:
        return 0.0


#指定日期的指数PB（等权重）
def get_index_pb_date(date):
    total_count = 0
    total_pb_sum = 0.0
    for code in index_code:
        stocks = get_index_stocks(code, date)
        q = query(valuation).filter(valuation.code.in_(stocks))
        df = get_fundamentals(q, date)
        if len(df) > 0:
            total_count += len(df)
            total_pb_sum += sum([1 / p if p > 0 else 0 for p in df.pb_ratio])
        else:
            total_count += float('NaN')
    if total_pb_sum > 0:
        return total_count / total_pb_sum
    else:
        return 0.0

    
#指数历史PEPB
def get_index_pe_pb():
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
        pe = get_index_pe_date(d)
        pb = get_index_pb_date(d)
        if pe > 0.0 and pb > 0.0:
            pes.append(get_index_pe_date(d))
            pbs.append(get_index_pb_date(d))
            average_pes.append(sum(pes) / len(pes))
            average_pbs.append(sum(pbs) / len(pbs))
            dates.append(d)
    d_pe = {
        'PE' : pd.Series(pes, index = dates),
        'AVERAGE_PE' : pd.Series(average_pes, index = dates),
    }
    d_pb = {
        'PB' : pd.Series(pbs, index = dates),
        'AVERAGE_PB' : pd.Series(average_pbs, index = dates),
    }
    PE = pd.DataFrame(d_pe)
    PB = pd.DataFrame(d_pb)
    return PE, PB


frames = pd.DataFrame()
today = pd.datetime.today()
results = []
index_name = u'全市场'

print index_name 

df_pe, df_pb = get_index_pe_pb()

pe = get_index_pe_date(today)
q_pes = [df_pe['PE'].quantile(i / 10.0) for i in range(11)]    
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
        '%.2f' % df_pe['AVERAGE_PE'][-1], 
        '%.2f' % (quantile_pe * 10)
    ] + 
    ['%.2f' % q for q in q_pes] + [df_pe['PE'].count()]
)
 
pb = get_index_pb_date(today)
q_pbs = [df_pb['PB'].quantile(i / 10.0)  for i in range(11)]
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
        '%.2f' % df_pb['AVERAGE_PB'][-1],
        '%.2f' % (quantile_pb * 10)
    ] + 
    ['%.2f' % q for q in q_pbs] + [df_pb['PB'].count()]
)

df_pe['10% PE'] = q_pes[1]
df_pe['30% PE'] = q_pes[3]
df_pe['50% PE'] = q_pes[5]
df_pe['90% PE'] = q_pes[9]

df_pb['10% PB'] = q_pbs[1]
df_pb['30% PB'] = q_pbs[3]
df_pb['50% PB'] = q_pbs[5]
df_pb['90% PB'] = q_pbs[9]

df_pe.plot(figsize = (18, 10),
           title = index_name + 'PE',
           style = ['m', 'k', 'g', 'c', 'y', 'r'])

df_pb.plot(figsize = (18, 10),
           title = index_name + 'PB',
           style = ['m', 'k', 'g', 'c', 'y', 'r'])

columns = [u'名称', u'当前日期', u'当前估值', u'平均估值', u'分位点%', u'最小估值'] + \
    ['%d%%' % (i * 10) for i in range(1, 10)] + [u'最大估值' , u"数据个数"]
df = pd.DataFrame(data = results, index = ['PE', 'PB'], columns = columns)
frames = pd.concat([frames, df])

frames
