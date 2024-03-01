import os
desired_path = "c:\\Users\\11930\\Desktop\\FINM 32900 Data Science Tools for Finance\\finm32900-final-project\\src"
os.chdir(desired_path) # 改变当前工作目录
print(os.getcwd())

import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Read monthly T-bill interest rates
df = pd.read_csv('Monthly T-bill Interest Rates.csv')

# Have a look at the data
df.head()

# Check column types
print(df.dtypes)

# Change date column to date format
df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')

# There are 'NC' values in 'Y20' column. Change these values to NaN and interpolate these points 
df['Y20'] = df['Y20'].replace('NC', np.nan)  # 将'NC'替换为NaN
df['Y20'] = df['Y20'].astype(float)  # 转换其他值为浮点数
df['Y20'] = df['Y20'].interpolate()  # 对NaN值进行插值

# Check if there is any NaN values in column 'Y20'
df['Y20'].isna().any()

# df['M01'] = df['M01'].interpolate()  # 对NaN值进行插值
# df['M03'] = df['M03'].interpolate()  # 对NaN值进行插值
# df['M06'] = df['M06'].interpolate()  # 对NaN值进行插值
# df['Y02'] = df['Y02'].interpolate()  # 对NaN值进行插值
# df['Y07'] = df['Y07'].interpolate()  # 对NaN值进行插值
# df['Y30'] = df['Y30'].interpolate()  # 对NaN值进行插值

df.head()

df.to_csv(r"Monthly T-bill.csv", index=False)

df = df.loc[237:,:].reset_index()

df

# Cubic Splines Interpolation

import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# 初始化一个空列表来存储每一行的插值结果
interpolated_results = []

periods = ['Y01', 'Y02', 'Y03', 'Y05', 'Y07', 'Y10', 'Y20', 'Y30']  # 期限列

# 定义期限的数值表示（月份转换为年）
maturity_numeric = np.array([1, 2, 3, 5, 7, 10, 20, 30])

# 循环遍历第344行之后的数据行
for index, row in df.iloc[342:].iterrows():
    # 提取每一行的利率数据，忽略日期，并尝试将数据转换为浮点数，无法转换的设置为NaN
    monthly_data = df.loc[index, periods].values
    
    # 创建立方样条插值函数
    cs = CubicSpline(maturity_numeric, monthly_data)

    # 创建用于插值的期限点
    maturity_interpolate = np.linspace(maturity_numeric.min(), maturity_numeric.max(), 59)

    # 计算插值利率并添加到结果列表
    interpolated_rates = cs(maturity_interpolate)
    interpolated_rates = np.insert(interpolated_rates, 0, df.loc[index, "M06"])
    # interpolated_results.append(df.loc[index, "M06"])
    interpolated_results.append(interpolated_rates)

interpolated_results = pd.DataFrame(interpolated_results)

# 假设 `interpolated_results` 是一个pandas DataFrame
new_columns = [f'Y{1+0.5*(i-1)}' for i in range(60)]
interpolated_results.columns = new_columns

interpolated_results.head()

# # 加上日期列并输出文件
# # 重新创建日期范围DataFrame，以确保其长度与interpolated_results_df相匹配
# date_range = pd.date_range(start='2001/7/1', end='2024/1/1', freq='MS')
# date_df = pd.DataFrame(date_range[:len(interpolated_results)], columns=['Date'])

# # 现在将日期DataFrame与插值结果DataFrame连接起来
# interpolated_results_date = pd.concat([date_df, interpolated_results], axis=1)

# interpolated_results_date.to_csv(r"interpolated_results_date.csv", index=False)
# interpolated_results.to_csv(r"interpolated_results.csv", index=False)


# Boostraping
from scipy.optimize import newton
import numpy as np

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
for i in range(271):
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

# Generate Output file: zero_rate_date

zero_rate = pd.DataFrame(zero_rate)

# 重新创建日期范围DataFrame，以确保其长度与interpolated_results_df相匹配
date_range = pd.date_range(start='2001/7/1', end='2024/1/1', freq='MS')
date_df = pd.DataFrame(date_range[:len(zero_rate)], columns=['Date'])

# 现在将日期DataFrame与插值结果DataFrame连接起来
zero_rate_date = pd.DataFrame(pd.concat([date_df, zero_rate], axis=1))

zero_rate.to_csv(r"zero_rate_date.csv", index=False)

zero_rate.head()
zero_rate_date.head()
