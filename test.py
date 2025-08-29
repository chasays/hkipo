import tushare as ts
import pandas as pd

# 设置 Tushare Token
ts.set_token('cc5124aa8e956b743b337b6023653ffba9fa3b0d3cdef4994930c69378ad')  # 请替换为您的 Tushare Token
pro = ts.pro_api()

# 获取新股上市信息
df = pro.new_share(start_date='20250101', end_date='20251231', market='HK')

# 数据预览
print(df.head())

# 保存为 CSV 文件
df.to_csv('chinaA_ipo_list.csv', index=False, encoding='utf-8-sig')
