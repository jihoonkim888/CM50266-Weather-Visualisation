import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('df_corr.csv')
# print(df)

# df for monthly...
df_month = df
df_month['Month'] = pd.DatetimeIndex(df['DateTime']).month
print(df_month)
print(df_month.groupby('Month').describe(include=np.number))
df_month_describe = df_month.groupby('Month').describe()[['mean', 'std', 'min', 'max']]
df_month_describe.to_csv('df_month_describe.csv', index=False)

# df for seasonal...
df_season = df_month
