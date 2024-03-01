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

file_path = DATA_DIR / 'manual' /'Monthly T-bill Interest Rates.csv'

# Read monthly T-bill interest rates
df = pd.read_csv(file_path)

# Have a look at the data
df.head()

# Check column types
print(df.dtypes)

# Change date column to date format
df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')

# There are 'NC' values in 'Y20' column. Change these values to NaN and interpolate these points 
df['Y20'] = df['Y20'].replace('NC', np.nan)  # turn 'NC' to NaN
df['Y20'] = df['Y20'].astype(float)  # turn other values as float
df['Y20'] = df['Y20'].interpolate()  # interpolate NaN values

# Check if there is any NaN values in column 'Y20'
df['Y20'].isna().any()

df = df.loc[341:,:].reset_index()
df

### Cubic Splines Interpolation

from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Initialize an empty list to store interpolated results
interpolated_results = []

periods = ['Y01', 'Y02', 'Y03', 'Y05', 'Y07', 'Y10', 'Y20', 'Y30']  # maturities

# Define numeric representations for maturities (in year)
maturity_numeric = np.array([1, 2, 3, 5, 7, 10, 20, 30])

# Loop through every row to interpolate yield rate
for index, row in df.iterrows():
    
    # Extract every row and corresponding columns
    monthly_data = df.loc[index, periods].values
    
    # Create cubic splines interpolation function
    cs = CubicSpline(maturity_numeric, monthly_data)

    # Create total number of maturities after interpolation
    maturity_interpolate = np.linspace(maturity_numeric.min(), maturity_numeric.max(), 59)

    # Derive the interpolation results
    interpolated_rates = cs(maturity_interpolate)
    
    # Add the half year ('M06') yield rate as the first column
    interpolated_rates = np.insert(interpolated_rates, 0, df.loc[index, "M06"])
    interpolated_results.append(interpolated_rates)

# Turn into a dataframe
interpolated_results = pd.DataFrame(interpolated_results)

# Rename columns
new_columns = [f'Y{1+0.5*(i-1)}' for i in range(60)]
interpolated_results.columns = new_columns

# Check output
interpolated_results


### Boostraping to create Treasury zero-coupon yield curve

# Import Newton's method to solve the equation
from scipy.optimize import newton

# Function to compute the price of the bond based on a given yield to maturity (r)
def bond_price(r, T, rates):
    M = 100  # Maturity value (face value of the bond)
    C = M * rates[T-1]/100 / 2  # Maturity value (face value of the bond)
    price = sum(C / ((1 + y/100/2)**(i+1)) for i, y in enumerate(rates[:T-1], start=0))
    price += (C + M) / ((1 + r/100/2)**T)
    return price

# Function to compute the difference from the bond's actual price (used for root finding)
def bond_price_difference(r, T, rates):
    return bond_price(r, T, rates) - 100  # The bond's actual price is 100

# Loop through each cell

zero_rate = []
for i in range(130, len(interpolated_results)):
    rates = interpolated_results.copy().loc[i,:]
    zero_rate_row = rates.copy()
    
    # We already have Y0.5 and Y1.0, start from Y1.5
    for j in range(2, len(zero_rate_row)):
        T = j + 1  # Convert the time to semi-annual periods
        initial_guess = rates[j]
        # Apply the Newton-Raphson method to find the zero-coupon rate
        zero_coupon_rate = newton(func=bond_price_difference, x0=initial_guess, args=(T, zero_rate_row))
        zero_rate_row[j] = zero_coupon_rate
    
    zero_rate.append(zero_rate_row)

### Generate Output file: zero_rate_date

zero_rate = pd.DataFrame(zero_rate).reset_index(drop=True)

# Create a series of dates corresponding to the results
date_range = pd.date_range(start='1992/7/1', end='2024/1/1', freq='MS')
date_df = pd.DataFrame(date_range[:len(zero_rate)], columns=['Date'])

# Concatenate the dates with 'zero_rate'
zero_rate_date = pd.DataFrame(pd.concat([date_df, zero_rate], axis=1))

# Define output path
output_file_path = OUTPUT_DIR / 'zero_rate_date.csv'

# Write the dataframe into a .csv file
zero_rate_date.to_csv(output_file_path, index=False)
