"""
This file constructs interpolated risk-free rate based on constant-maturity Treasury yields.

1. First, NaN values are filled using linear interpolation method;

2. Second, cubic splines method is used to derive interpolated risk-free rates for maturities
every month during 1 month to 360 months.
"""

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
from scipy.interpolate import CubicSpline

def construct_rf():
    file_path = DATA_DIR / 'manual' /'Monthly Treasury Yield.csv'

    # Read monthly T-bill interest rates
    df = pd.read_csv(file_path)

    df['Date'] = pd.to_datetime(df['Date'])

    convert_numeric = ['M01', 'M03', 'M06', 'Y01', 'Y02', 'Y03', 'Y05', 'Y07', 'Y10', 'Y20', 'Y30']
    for column in convert_numeric:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Interpolate df to get rf in each month
    df[convert_numeric] = df[convert_numeric].interpolate(method='linear', axis=1, limit_direction='both')


    # Initialize an empty list to store interpolated results
    interpolated_results = []

    periods = ['M01', 'M03', 'M06', 'Y01', 'Y02', 'Y03', 'Y05', 'Y07', 'Y10', 'Y20', 'Y30']  # maturities

    # Define numeric representations for maturities (in year)
    maturity_numeric = np.array([1/12, 3/12, 6/12, 1, 2, 3, 5, 7, 10, 20, 30])

    # Loop through every row to interpolate yield rate
    for index, row in df.iterrows():
        
        # Extract every row and corresponding columns
        monthly_data = df.loc[index, periods].values
        
        # Create cubic splines interpolation function
        cs = CubicSpline(maturity_numeric, monthly_data)

        # Create total number of maturities after interpolation
        maturity_interpolate = np.linspace(maturity_numeric.min(), maturity_numeric.max(), 360)

        # Derive the interpolation results
        interpolated_rates = cs(maturity_interpolate)
        
        interpolated_results.append(interpolated_rates)

    # Turn into a dataframe
    interpolated_results = pd.DataFrame(interpolated_results)

    # Rename columns
    new_columns = [f'M{i+1}' for i in range(360)]
    interpolated_results.columns = new_columns

    # Create a series of dates corresponding to the results
    date_range = pd.date_range(start='1953/4/1', end='2024/1/1', freq='MS')
    date_df = pd.DataFrame(date_range[:len(interpolated_results)], columns=['Date'])

    # Concatenate the dates with 'zero_rate'
    interpolated_results = pd.DataFrame(pd.concat([date_df, interpolated_results], axis=1))

    return interpolated_results


if __name__ == "__main__":
    
    # Call functions
    df_rf = construct_rf()

    # Export output
    df_rf.to_csv(OUTPUT_DIR / "Interpolated_Rf.csv", index=False)
