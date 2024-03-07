import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt

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

end_date = datetime(2012, 12, 31)
df_raw = CBreturn.replicate_columns(df_b, end_date)

# Import Data for Comparison
df_expected = pd.read_csv(f'{DATA_DIR}/manual/He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv')


def test_df_cb_columns():
    # Columns for testing
    df_expected = df_expected[['yyyymm',
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',	
        'US_bonds_17',	'US_bonds_18',
        'US_bonds_19',	'US_bonds_20',
    ]]

    # Specify the time range to test
    start_date = datetime(2003, 9, 1)
    end_date = datetime(2003, 12, 31)

    # filter the time range - df_expected
    df_expected['yyyymm'] = pd.to_datetime(df_expected['yyyymm'], format='%Y%m')
    subset_expected = df_expected[(df_expected['yyyymm'] >= start_date) & (df_expected['yyyymm'] <= end_date)] 

    # filter the time range - df_raw
    df_raw['date'] = df_raw['date'].dt.to_timestamp()
    subset_actual = df_raw[(df_raw['date'] >= start_date) & (df_raw['date'] <= end_date)] 

    print(subset_expected)
    print(subset_actual)

    # graph
    #plt.plot(subset_actual['date'], subset_actual['US_bonds_11'], linestyle='-', color='red')
    #plt.plot(subset_expected['yyyymm'], subset_expected['US_bonds_11'], linestyle='-', color='green')
    #plt.title('Line Plot of US bond1 Over Time')
    #plt.ylabel('US bond1 Values')
    #plt.xlabel('Date')
    #plt.grid(True)
    #plt.show()

    # Test for equality of specific rows within the specified tolerance?!
    tolerance = 0.05
    # Convert DataFrame values to float64
    expected_values = subset_expected.drop('yyyymm', axis=1).values.astype(np.float64)
    actual_values = subset_actual.drop('date', axis=1).values.astype(np.float64)
    assert np.all(np.isclose(expected_values, actual_values, rtol=tolerance, atol=tolerance)), "DataFrames are not equal within the tolerance range."





