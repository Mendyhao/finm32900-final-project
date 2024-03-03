import pandas as pd
import os
import numpy as np

'''
README

What next:
please check the coding part;
maybe convert into def or seperate them into deferent files;
please add the filter part, refer to the high light lines in google file;
please add them to github

Dataset:
1) I'm now using y0189(yhe year 1989) to writing the code. If you want to generate the complete data, please using folder "data".
2) ok
3) ok


'''

# 1) Lehman
folder_path = './data'
column_widths = [8, 31, 10, 10, 9, 2, 8, 8, 8, 8, 10, 7, 2, 1, 7, 1, 7, 7, 3, 2, 1, 7, 2]
files = os.listdir(folder_path)
dfs = []

for file in files:
    file_path = os.path.join(folder_path, file)
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            start = 0
            row = []
            for width in column_widths:
                value = line[start:start+width].strip()
                row.append(value)
                start += width
            data.append(row)
    df = pd.DataFrame(data)
    dfs.append(df)
    dfL = pd.concat(dfs, axis=0)

'''
cusip        a8    CUSIP
date         i8    Date
fprc       f7.3    Flat Pice (bid)
cp         f7.4    Coupon
yld        f6.3  * Yield
'''
column_indices = [0, 2, 6, 8, 9 ]
dfL = dfL[column_indices]

stdL = ['id', 'date', 'price', 'coupon', 'yield']
dfL = dfL.rename(columns=dict(zip(dfL.columns, stdL)))



# 2) TRACE
file_path_T = './TRACE.csv'
columns_T = ['DATE', 'CUSIP', 'PRICE_L5M', 'COUPON', 'YIELD']
dfT = pd.read_csv(file_path_T, usecols=columns_T)

stdT = ['date', 'id', 'coupon', 'yield', 'price']
dfT = dfT.rename(columns=dict(zip(dfT.columns, stdT)))



# 3) Mergent
file_path_M = './fzwsx7pyydymhs9q.csv'
columns_M = ['complete_cusip', 'flat_price', 'accrued_interest', 'OFFERING_YIELD','trans_date']
dfM = pd.read_csv(file_path_M, usecols=columns_M)

stdM = ['id', 'price', 'coupon', 'date', 'yield']
dfM = dfM.rename(columns=dict(zip(dfM.columns, stdM)))



# datatype
dfL['date'] = pd.to_datetime(dfL['date'], format='%Y%m%d')
dfT['date'] = pd.to_datetime(dfT['date'], format='%Y-%m-%d')
dfM['date'] = pd.to_datetime(dfM['date'], format='%Y-%m-%d')

dfT['yield'] = dfT['yield'].str.rstrip('%')
convert_float = ['yield', 'coupon', 'price']
dfL[convert_float] = dfL[convert_float].apply(pd.to_numeric, errors='coerce')
dfT[convert_float] = dfT[convert_float].apply(pd.to_numeric, errors='coerce')
dfM[convert_float] = dfM[convert_float].apply(pd.to_numeric, errors='coerce')

    #check
print(dfL)
print(dfT)
print(dfM)



# Merge 1)&2)
df_merge_12 = pd.concat([dfL, dfT], axis=0)
print(df_merge_12)



# Fillna by 3)
df_merge = pd.concat([df_merge_12, dfM], axis=0)
df_merge = df_merge.sort_values('date').drop_duplicates(['id', 'date'], keep='last')
print(df_merge)

    #check
count_duplicates = df_merge.groupby(['id', 'date']).size().reset_index(name='count')
print(count_duplicates)
count_duplicates['count'].value_counts()



# Drop corporate price below on cent per dollar
df_drop = df_merge[~(df_merge['price'] < 0.01)]
print(df_drop)



# Calculate return
df_sorted = df_drop.sort_values('date', ascending=True).reset_index(drop=True)
df_sorted['date'].is_monotonic_increasing

    #check
df_drop.iloc[10086]
df_sorted.loc[(df_sorted['date'] == df_drop.iloc[10086]['date']) & (df_sorted['id'] == df_drop.iloc[10086]['id'])]

grouped = df_sorted.groupby('id')
df_sorted['return'] = grouped.apply(lambda x:(x['price'] + x['coupon']) / x['price'].shift(1)).reset_index(level=0, drop=True)
    #check
print(df_sorted)
df_sorted['return'].value_counts()
df_sorted.isna().sum()
df_sorted.describe()



# Remove bounceback
df_b = df_sorted.sort_values(['id', 'date'])
indices_to_remove = []
for _, group in df_b.groupby('id'):
    product = group['return'].shift(1) * group['return']
    mask = product < -0.04
    indices_to_remove.extend(group.loc[mask].index)
df_remove = df_b.drop(indices_to_remove)
df_b = df_remove.reset_index(drop=True)
    #check
print(df_b)
df_b['return'].value_counts()
df_b['return'].isna().sum()
df_b['return'].describe()



# Calculate log return
df_b['log_return'] = np.log(df_sorted['return'])
df_b = df_b.dropna(subset=['log_return'])
    #check
df_b.describe()



# Calculate sum
df_sum = df_b.dropna(subset=['yield'])
df_sum['group'] = pd.qcut(df_sum['yield'], q=10, labels=False)
group_means = df_sum.groupby(['date', 'group'])['log_return'].mean().reset_index()
result = group_means.pivot(index='date', columns='group', values='log_return').reset_index()
print(result)
rename = result.columns[1:]
new_column_names = ['US_bonds_{:02d}'.format(i+1) for i in range(len(rename))]
columns_mapping = dict(zip(rename, new_column_names))
result.rename(columns=columns_mapping, inplace=True)