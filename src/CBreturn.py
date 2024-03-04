'''
README

What next:
please check the coding part; (checked -- Mengdi Hao)
maybe convert into def or seperate them into deferent files; (separated into functions -- Mengdi Hao)
please add the filter part, refer to the high light lines in google file; (TO BE DONE)
please add them to github

Dataset path:
1) Lehman Brothers dataset: data/manual/Lehman data
2) TRACE dataset: data/'TRACE.csv'
3) Mergent FISD/NAIC dataset: data/'Mergent.csv'
'''

import os
from pathlib import Path

# Derive current working directory
current_dir = Path(os.getcwd())

# If current working directory is not 'src', update it
if current_dir.stem != 'src':
    src_directory = current_dir / 'src'
    os.chdir(src_directory)

import config

OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)


import pandas as pd
import numpy as np

def combine_Lehman():
    # 1) Lehman
    folder_path = DATA_DIR / 'Lehman data'
    column_widths = [8, 31, 10, 10, 9, 2, 8, 8, 8, 8, 10, 7, 2, 1, 7, 1, 7, 7, 3, 2, 1, 7, 2]
    files = os.listdir(folder_path)
    dfs = []

    # Useful columns
    column_indices = [0, 2, 6, 8, 9]

    dfs = []  # used to store the dataframe in each single file

    for file in files:
        file_path = os.path.join(folder_path, file)
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                start = 0
                row = []
                for i, width in enumerate(column_widths):
                    if i in column_indices:
                        value = line[start:start+width].strip()
                        row.append(value)
                    start += width
                data.append(row)
        df = pd.DataFrame(data, columns=column_indices)  # only keep useful columns
        dfs.append(df)

    dfL = pd.concat(dfs, axis=0)  # concatenate all dataframes into one large dataframe
    '''
    cusip        a8    CUSIP
    date         i8    Date
    fprc       f7.3    Flat Pice (bid)
    cp         f7.4    Coupon
    yld        f6.3  * Yield
    '''
    stdL = ['id', 'date', 'price', 'coupon', 'yield']
    dfL = dfL.rename(columns=dict(zip(dfL.columns, stdL)))
    dfL['date'] = pd.to_datetime(dfL['date'], format='%Y%m%d')
    convert_float = ['yield', 'coupon', 'price']
    dfL[convert_float] = dfL[convert_float].apply(pd.to_numeric, errors='coerce')

    return dfL

def read_trace():
    # 2) TRACE
    file_path_T = DATA_DIR / 'TRACE.csv'
    columns_T = ['DATE', 'CUSIP', 'PRICE_L5M', 'COUPON', 'YIELD']
    dfT = pd.read_csv(file_path_T, usecols=columns_T)

    stdT = ['date', 'id', 'coupon', 'yield', 'price']
    dfT = dfT.rename(columns=dict(zip(dfT.columns, stdT)))
    dfT['date'] = pd.to_datetime(dfT['date'], format='%Y-%m-%d')
    dfT['yield'] = dfT['yield'].str.rstrip('%')
    convert_float = ['yield', 'coupon', 'price']
    dfT[convert_float] = dfT[convert_float].apply(pd.to_numeric, errors='coerce')

    return dfT

def read_mergent():
    file_path_M = DATA_DIR / 'Mergent.csv'
    columns_M = ['complete_cusip', 'flat_price', 'accrued_interest', 'OFFERING_YIELD', 'trans_date', 'COUPON_TYPE', 'OVERALLOTMENT_OPT', 'PUTABLE']
    dfM = pd.read_csv(file_path_M, usecols=columns_M)

    stdM = ['id', 'price', 'coupon', 'date', 'yield', 'type', 'over_opt', 'putable']
    dfM = dfM.rename(columns=dict(zip(dfM.columns, stdM)))

    try:
        dfM['date'] = pd.to_datetime(dfM['date'], format='%Y-%m-%d')
    except ValueError:
        print("Error converting date. Setting to default value.")
        # Handle the error by setting the date to a default value or taking other actions
        dfM['date'] = pd.to_datetime('1900-01-01')  # Adjust the default date as needed

    convert_float = ['yield', 'coupon', 'price']
    dfM[convert_float] = dfM[convert_float].apply(pd.to_numeric, errors='coerce')

    return dfM

def merge_and_fillna(dfL, dfT, dfM):
    # Merge 1)&2)
    df_merge_12 = pd.concat([dfL, dfT], axis=0)

    # Fillna by 3)

    # Merge df_merge_12 and dfM based on id and data
    df_merge = pd.merge(df_merge_12, dfM, on=['id', 'date'], how='left', suffixes=('', '_from_dfM'))

    # Loop through columns to update NaN values using values from dfM
    for col in df_merge.columns:
        if '_from_dfM' in col:
            original_col = col.replace('_from_dfM', '')
            df_merge[original_col] = df_merge[original_col].fillna(df_merge[col])
            df_merge.drop(columns=col, inplace=True)  # delete helper column

    return df_merge

def data_cleaning(df_merge):
    
    # 1. Drop corporate price below on cent per dollar
    df_drop = df_merge[~(df_merge['price'] < 0.01)]
    print(df_drop)

    # 3. Remove bounceback

    df_drop = df_drop[
        (df_drop['type'] != 'Z') &
        (df_drop['over_opt'] != 'Y') &
        (df_drop['putable'] != 'Y')
    ]
    
    columns_to_drop = ['price_from_dfM', 'coupon_from_dfM', 'yield_from_dfM', 'type', 'over_opt', 'putable']
    df_drop = df_drop.drop(columns=columns_to_drop)

    # Calculate return
    df_sorted = df_drop.sort_values('date', ascending=True).reset_index(drop=True)
    df_sorted['date'].is_monotonic_increasing
    grouped = df_sorted.groupby('id')
    df_sorted['return'] = grouped.apply(lambda x:(x['price'] + x['coupon']) / x['price'].shift(1)).reset_index(level=0, drop=True)

    # Remove rows of adjacent returns whose product is less than -0.04
    df_b = df_sorted.sort_values(['id', 'date'])
    indices_to_remove = []

    for _, group in df_b.groupby('id'):
        product = group['return'].shift(1) * group['return']
        mask = product < -0.04
        indices_to_remove.extend(group.loc[mask].index)

    df_remove = df_b.drop(indices_to_remove)
    df_b = df_remove.reset_index(drop=True)

    return df_b

def replicate_columns(df_b):
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

    return result

if __name__ == "__main__":
    
    # Call functions
    dfL = combine_Lehman()
    dfT = read_trace()
    dfM = read_mergent()
    df_merge = merge_and_fillna(dfL, dfT, dfM)
    df_b = data_cleaning(df_merge)
    
    result = replicate_columns(df_b)
    result.to_csv(OUTPUT_DIR / 'Corporate Bond Return Replicated.csv', index=False)  # export output to specified path

