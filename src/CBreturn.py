'''
README

What next:
please check the coding part; (checked -- Mengdi Hao) (checked -- Mengdi Hao)
maybe convert into def or seperate them into deferent files; (separated into functions -- Mengdi Hao) (separated into functions -- Mengdi Hao)
please add the filter part, refer to the high light lines in google file; (TO BE DONE) (TO BE DONE)
please add them to github

Dataset path:
1) Lehman Brothers dataset: data/manual/Lehman data
2) TRACE dataset: data/'TRACE.csv'
3) Mergent FISD/NAIC dataset: data/'Mergent.csv'
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
        r'.*?\s+'              # skip mdate column
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
        columns = ['cusip', 'date', 'fprc', 'cp', 'yld']
        df = pd.DataFrame(data, columns=columns)
        dfs.append(df)

    # concatenate all dataframes into a large dataframe
    dfL = pd.concat(dfs, axis=0, ignore_index=True)

    # convert date format
    dfL['date'] = pd.to_datetime(dfL['date'], format='%Y%m%d', errors='coerce')

    # convert numbers to numeric format
    convert_float = ['fprc', 'cp', 'yld']
    dfL[convert_float] = dfL[convert_float].apply(pd.to_numeric, errors='coerce')

    stdL = ['id', 'date', 'price', 'coupon', 'yield']
    dfL = dfL.rename(columns=dict(zip(dfL.columns, stdL)))
    
    return dfL

def read_trace():
    # 2) TRACE
    file_path_T = DATA_DIR / 'TRACE.csv'
    dfT = pd.read_csv(file_path_T)
    dfT['yield'] = dfT['yield']*100 # data automatically collected

    stdT = ['date', 'id', 'price', 'coupon', 'yield']
    dfT = dfT.rename(columns=dict(zip(dfT.columns, stdT)))
    dfT['date'] = pd.to_datetime(dfT['date'], format='%Y-%m-%d')

    # dfT['yield'] = dfT['yield'].str.rstrip('%')
    convert_float = ['yield', 'coupon', 'price']
    dfT[convert_float] = dfT[convert_float].apply(pd.to_numeric, errors='coerce')

    return dfT

def read_mergent():
    # 3) Mergent
    file_path_M = DATA_DIR / 'Mergent.csv'
    dfM = pd.read_csv(file_path_M)
    
    # Rename columns
    stdM = ['id', 'price', 'coupon', 'date']
    dfM = dfM.rename(columns=dict(zip(dfM.columns, stdM)))
    

    # Change data types
    convert_float = ['coupon', 'price']
    dfM[convert_float] = dfM[convert_float].apply(pd.to_numeric, errors='coerce')

    # Deal with "date"
    dfM['date'] = pd.to_datetime(dfM['date'], format='%Y-%m-%d', errors = 'coerce')
    #If there are multiple rows within one month, aggregate the data and calculate the mean
    dfM = dfM.groupby(['id', dfM['date'].dt.to_period("M")]).agg({'coupon': 'mean', 'price': 'mean'}).reset_index()

    return dfM


def merge_and_fillna(dfL, dfT, dfM):
    # Merge 1)&2)
    df_merge_12 = pd.concat([dfL, dfT], axis=0)
    df_merge_12['date']= df_merge_12['date'].dt.to_period('M')

    # Fillna by 3)
    # Merge df_merge_12 and dfM based on id and data
    df_merge = pd.merge(df_merge_12, dfM, on=['id', 'date'], how='outer', suffixes=('', '_from_dfM'))

    # Loop through columns to update NaN values using values from dfM
    for col in df_merge.columns:
        if '_from_dfM' in col:
            original_col = col.replace('_from_dfM', '')
            df_merge[original_col] = df_merge[original_col].fillna(df_merge[col])
            df_merge.drop(columns=col, inplace=True)  # delete helper column

    return df_merge

def data_cleaning(df_merge):
    
    # Drop corporate price below on cent per dollar
    df_drop = df_merge[~(df_merge['price'] < 0.01)]
    print(df_drop)

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


def replicate_columns(df_b, end_date):
    # Calculate log return
    df_b['log_return'] = np.log(df_b['return'])
    df_b = df_b.dropna(subset=['log_return'])

    # Calculate sum
    #df_sum = df_b.dropna(subset=['yield'])

    #Filter by Date
    end_date_period = pd.to_datetime(end_date).to_period("M")
    df_sum = df_b[df_b['date']<=end_date_period]

    # Sort portfolios by yield
    yield_means = df_sum.groupby('id')['yield'].mean() 
    df_sum['mean_yield'] = df_sum['id'].map(yield_means)
    df_sum['group'] = pd.qcut(df_sum['mean_yield'], q=10, labels=False)
    #df_sum['group'] = pd.qcut(df_sum['yield'], q=10, labels=False)

    group_means = df_sum.groupby(['date', 'group'])['return'].mean().reset_index()
    result = group_means.pivot(index='date', columns='group', values='return').reset_index()
    
    # Rename the columns
    rename = result.columns[1:]
    new_column_names = ['US_bonds_{:02d}'.format(i+11) for i in range(len(rename))]
    columns_mapping = dict(zip(rename, new_column_names))
    result.rename(columns=columns_mapping, inplace=True)

    # Adjust the display format of the return values to match "He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv"
    # ex. from 1% to 0.01
    columns = [
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',	
        'US_bonds_17',	'US_bonds_18',
        'US_bonds_19',	'US_bonds_20',
    ]
    result[columns] = result[columns]/100

    return result

if __name__ == "__main__":
    # Call functions
    dfL = combine_Lehman()
    dfT = read_trace()
    dfM = read_mergent()
    df_merge = merge_and_fillna(dfL, dfT, dfM)
    df_b = data_cleaning(df_merge)

    # Update Dataframe Until Now
    end_date = datetime(2023, 12, 31)
    result = replicate_columns(df_b, end_date)
    result.to_csv(OUTPUT_DIR / 'Corporate Bond Return Replicated.csv', index=False)  # export output to specified path
