import pandas as pd
from pandas.testing import assert_frame_equal
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

    # Specify the time range - sample data
    condition = ((df_expected['yyyymm'] >= 201001) & (df_expected['yyyymm'] <= 201004))
    subset_expected = df_expected[condition]

    # Specify the time range - df_raw
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2010, 4, 30)
    columns = [
        'US_bonds_11', 'US_bonds_12',
        'US_bonds_13',	'US_bonds_14',
        'US_bonds_15',	'US_bonds_16',	
        'US_bonds_17',	'US_bonds_18',
        'US_bonds_19',	'US_bonds_20',
    ]
    subset_actual = df_raw[(df_raw['date'] >= start_date) & (df_raw['date'] <= end_date)] 
    subset_actual[columns] = subset_actual[columns]/100

    # Test for equality of specific rows within the specified tolerance, ignoring column names
    assert (subset_expected.values == subset_actual.values).all(), "DataFrames are not equal"



