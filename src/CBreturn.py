'''
README

This file loads the three datasets (Lehman, TRACE, Mergent), conducts data cleaning process, calculates excess return,
and replicate He_Kelly's result

Dataset path:
1) Lehman Brothers dataset: data/'manual'/Lehman data
2) TRACE dataset: data/'TRACE.csv'
3) Mergent FISD/NAIC dataset: data/ 'manual'/'Mergent.csv'
'''

import os
from pathlib import Path
from datetime import datetime

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
import os
import re
from pathlib import Path

def combine_Lehman():

    folder_path = DATA_DIR / 'manual/Lehman data'

    # Define regular expression pattern, only match needed columns
    pattern = re.compile(
        r'(\S{8})\s+'          # cusip
        r'.*?\s{2,}'           # skip name column
        r'(\d{8})\s+'          # date
        r'.*?\s+'              # skip idate 
        r'(\d{8})\s+'          # mdate
        r'.*?\s+'              # skip tdrmtx column
        r'(-?\d+\.\d{3})\s+'   # fprc
        r'.*?\s+'              # skip aint column
        r'(-?\d+\.\d{4})\s+'   # cp
        r'(-?\d+\.\d{3})\s+'   # yld
    )
    
    files = os.listdir(folder_path)
    dfs = []

    for file in files:
        file_path = os.path.join(folder_path, file)
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    # extract interested columns only
                    data.append(match.groups())
                    
        # specify columns
        columns = ['cusip', 'date', 'maturity', 'fprc', 'cp', 'yld']
        df = pd.DataFrame(data, columns=columns)
        dfs.append(df)

    # concatenate all dataframes into a large dataframe
    dfL = pd.concat(dfs, axis=0, ignore_index=True)

    # convert date format
    dfL['date'] = pd.to_datetime(dfL['date'], format='%Y%m%d', errors='coerce')
    dfL['maturity'] = pd.to_datetime(dfL['maturity'], format='%Y%m%d', errors='coerce')
    dfL = dfL.dropna(subset=['maturity'])

    # convert numbers to numeric format
    convert_float = ['fprc', 'cp', 'yld']
    dfL[convert_float] = dfL[convert_float].apply(pd.to_numeric, errors='coerce')

    # Calculate month_to_maturity 
    dfL['month_to_maturity'] = (dfL['maturity'].dt.to_period('M') - dfL['date'].dt.to_period('M')).apply(lambda x: x.n)
    
    dfL = dfL[dfL['month_to_maturity'] <= 360]


    stdL = ['id', 'date', 'maturity', 'price', 'coupon', 'yield', 'month_to_maturity']
    dfL = dfL.rename(columns=dict(zip(dfL.columns, stdL)))
    
    return dfL

def read_trace():
    # 2) TRACE
    file_path_T = DATA_DIR / 'TRACE.csv'
    dfT = pd.read_csv(file_path_T)
    dfT['yield'] = dfT['yield']*100 # data automatically collected

    stdT = ['date', 'id', 'price', 'coupon', 'yield', 'maturity']
    dfT = dfT.rename(columns=dict(zip(dfT.columns, stdT)))
    dfT['date'] = pd.to_datetime(dfT['date'], format='%Y-%m-%d')
    dfT['maturity'] = pd.to_datetime(dfT['maturity'], format='%Y-%m-%d')

    # dfT['yield'] = dfT['yield'].str.rstrip('%')
    convert_float = ['yield', 'coupon', 'price']
    dfT[convert_float] = dfT[convert_float].apply(pd.to_numeric, errors='coerce')

    # Calculate month_to_maturity
    dfT['month_to_maturity'] = (dfT['maturity'].dt.to_period('M') - dfT['date'].dt.to_period('M')).apply(lambda x: x.n)
    dfT = dfT[dfT['month_to_maturity'] <= 360]


    return dfT

def read_mergent():
    # 3) Mergent
    file_path_M = DATA_DIR / 'manual' / 'Mergent_part.csv'
    dfM = pd.read_csv(file_path_M)
    
    # Rename columns
    stdM = ['id', 'price', 'coupon', 'date', 'maturity', 'yield']
    dfM = dfM.rename(columns=dict(zip(dfM.columns, stdM)))
    

    # Change data types
    convert_float = ['coupon', 'price', 'yield']
    dfM[convert_float] = dfM[convert_float].apply(pd.to_numeric, errors='coerce')

    # Deal with "date"
    dfM['date'] = pd.to_datetime(dfM['date'], format='%Y-%m-%d', errors = 'coerce')
    dfM['maturity'] = pd.to_datetime(dfM['maturity'], format='%Y-%m-%d', errors = 'coerce')
    
    # Filter useful rows in Mergent dataset
    # start_date = pd.Timestamp('1998-04-01')
    # end_date = pd.Timestamp('2002-06-30')
    # dfM = dfM[(dfM['date'] >= start_date) & (dfM['date'] <= end_date)]

    # Only keep rows where the day is the latest in each month
    dfM = dfM.groupby([dfM['id'], dfM['date'].dt.year, dfM['date'].dt.month]).apply(lambda x: x.loc[x['date'].idxmax()])
    dfM = dfM.reset_index(drop=True)
    dfM = dfM.dropna(subset=['maturity'])

    # Calculate month_to_maturity
    dfM['month_to_maturity'] = (dfM['maturity'].dt.to_period('M') - dfM['date'].dt.to_period('M')).apply(lambda x: x.n)
    dfM = dfM[dfM['month_to_maturity'] <= 360]
    # dfM['maturity'].isna().sum()

    return dfM

def merge_and_fillna(dfL, dfT, dfM):
    # Merge 1)&2)&3)
    df_merge = pd.concat([dfL, dfT, dfM], axis=0)

    return df_merge

def data_cleaning(df_merge):
    
    # 1. Drop corporate price below on cent per dollar
    df_drop = df_merge[~(df_merge['price'] < 0.01)]
    
    # 2. Remove rows of adjacent returns whose product is less than -0.04
    # Calculate return
    df_sorted = df_drop.sort_values('date', ascending=True).reset_index(drop=True)
    df_sorted['date'].is_monotonic_increasing
    grouped = df_sorted.groupby('id')
    df_sorted['return'] = grouped.apply(lambda x:(x['price'] + x['coupon']) / x['price'].shift(1)).reset_index(level=0, drop=True)

    # Remove rows of adjacent returns whose product is less than -0.04
    df_b = df_sorted.sort_values(['id', 'date'])
    indices_to_remove = []

    # The following code is commented out because previous running result shows that there is no such case
    # You can check by bringing these code back
    
    # for _, group in df_b.groupby('id'):
    #     product = group['return'].shift(1) * group['return']
    #     mask = product < -0.04
    #     indices_to_remove.extend(group.loc[mask].index)

    df_remove = df_b.drop(indices_to_remove)
    df_b = df_remove.reset_index(drop=True)

    return df_b

def minus_rf(df_b):

    df_b['year_month'] = df_b['date'].dt.to_period('M')

    # Load interpolated rf rate
    rf_rates_df = pd.read_csv(OUTPUT_DIR / 'Interpolated_Rf.csv')
    rf_rates_df['Date'] = pd.to_datetime(rf_rates_df['Date'])
    rf_rates_df['year_month'] = rf_rates_df['Date'].dt.to_period('M')

    # Change rf to long format
    rf_long_df = rf_rates_df.melt(id_vars=['Date', 'year_month'], var_name='month', value_name='rf_rate')
    rf_long_df['month_to_maturity'] = rf_long_df['month'].str.replace('M', '').astype(int)

    # Merge df_b and rf based on year_month and month_to_maturity
    merged_df = df_b.merge(rf_long_df, on=['year_month', 'month_to_maturity'], how='left')

    merged_df['excess_return'] = np.log(merged_df['return']) - np.log(merged_df['rf_rate']/100+1)
    merged_df = merged_df.dropna(subset=['excess_return'])

    # Calculate yield spread
    merged_df['yield_spread'] = merged_df['yield'] - merged_df['rf_rate']

    df_minus = merged_df

    return df_minus

def replicate_columns(df_minus, end_date):
    
    df_sum = df_minus[df_minus['date']<=end_date]

    df_sum = df_sum.dropna(subset=['yield_spread'])
    df_sum['date'] = df_sum['date'].dt.to_period("M")

    # Sort portfolios by yield_spread
    df_sum['group'] = df_sum.groupby('date')['yield_spread'].transform(lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))

    # Calculate average value of excess_return for each group
    grouped = df_sum.groupby(['date', 'group'])['excess_return'].mean().reset_index()

    # Derive result
    result = grouped.pivot(index='date', columns='group', values='excess_return')

    result = result.reset_index()
    
    # Rename the columns
    rename = result.columns[1:]
    new_column_names = ['US_bonds_{:02d}'.format(i+11) for i in range(len(rename))]
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
    df_minus = minus_rf(df_b)

    # Update Dataframe Until Now
    end_date = datetime(2023, 12, 31)
    result = replicate_columns(df_minus, end_date)
    result.to_csv(OUTPUT_DIR / 'Corporate Bond Return Replicated.csv', index=False)  # export output to specified path




