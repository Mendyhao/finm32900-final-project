import pandas as pd
from datetime import datetime
import numpy as np
import os
from pathlib import Path


# Derive current working directory
current_dir = Path(os.getcwd())

# If current working directory is not 'src', update it
if current_dir.stem != 'src':
    src_directory = current_dir / 'src'
    os.chdir(src_directory)

import CBreturn
import config
DATA_DIR = config.DATA_DIR

# Import Coporate Bond Return Data
dfL = CBreturn.combine_Lehman()
dfT = CBreturn.read_trace()
dfM = CBreturn.read_mergent()
df_merge = CBreturn.merge_and_fillna(dfL, dfT, dfM)
df_b = CBreturn.data_cleaning(df_merge)
df_minus = CBreturn.minus_rf(df_b)

end_date = datetime(2012, 12, 31)
df_raw = CBreturn.replicate_columns(df_minus, end_date)

# Import Data for Comparison
df_expected = pd.read_csv(f'{DATA_DIR}/manual/He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv')



# Test if the data we replicate is similar to the sample data for a short period of time
def test_df_cb_columns():
    # Select columns for testing
    df_expected = df_expected[['yyyymm',
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',
    ]]

    df_raw = df_raw[['date',
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',	
    ]]

    # Specify the time range to test
    start_date = datetime(2003, 9, 1)
    end_date = datetime(2003, 12, 31)

    # Filter the time range for df_expected
    df_expected['yyyymm'] = pd.to_datetime(df_expected['yyyymm'], format='%Y%m')
    subset_expected = df_expected[(df_expected['yyyymm'] >= start_date) & (df_expected['yyyymm'] <= end_date)] 

    # Filter the time range for df_raw
    df_raw['date'] = df_raw['date'].dt.to_timestamp()
    subset_actual = df_raw[(df_raw['date'] >= start_date) & (df_raw['date'] <= end_date)] 

    # Set the tolerance to 0.05 (5%) for data comparison
    expected_values = subset_expected.drop('yyyymm', axis=1).values.astype(np.float64)
    actual_values = subset_actual.drop('date', axis=1).values.astype(np.float64)
    assert np.all(np.isclose(expected_values, actual_values, rtol=5e-2, atol=5e-2)), "DataFrames are not equal within the tolerance range."



# Test the mean from 1975-1997 (longer period of time)
def test_df_cb_mean():
    # Select columns for testing
    df_expected = df_expected[['yyyymm',
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',
        'US_bonds_17',	'US_bonds_18',
        'US_bonds_19',	'US_bonds_20',
    ]]

    df_raw = df_raw[['date',
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',
        'US_bonds_17',	'US_bonds_18',
        'US_bonds_19',	'US_bonds_20',	
    ]]

    # Specify the time range to test
    start_date = datetime(1975, 1, 1)
    end_date = datetime(1997, 12, 31)

    # Filter the time range for df_expected
    df_expected['yyyymm'] = pd.to_datetime(df_expected['yyyymm'], format='%Y%m')
    subset_expected = df_expected[(df_expected['yyyymm'] >= start_date) & (df_expected['yyyymm'] <= end_date)] 

    # Filter the time range for df_raw
    df_raw['date'] = df_raw['date'].dt.to_timestamp()
    subset_actual = df_raw[(df_raw['date'] >= start_date) & (df_raw['date'] <= end_date)] 

    # Calculate and assign the mean to a new column
    subset_expected['mean'] = subset_expected.iloc[:, 1:].mean(axis=1)
    subset_actual['mean'] = subset_actual.iloc[:, 1:].mean(axis=1)

    # Set the tolerance to 0.04 (4%) for mean comparison (smaller tolerance)
    assert np.all(np.isclose(subset_expected['mean'], subset_actual['mean'], rtol=4e-2, atol=4e-2)), "DataFrames are not equal within the tolerance range."

