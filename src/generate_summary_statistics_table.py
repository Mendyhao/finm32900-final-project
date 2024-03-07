import pandas as pd
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
OUTPUT_DIR = Path(config.OUTPUT_DIR)

# Import Coporate Bond Return Data
dfL = CBreturn.combine_Lehman()
dfT = CBreturn.read_trace()
dfM = CBreturn.read_mergent()
df_merge = CBreturn.merge_and_fillna(dfL, dfT, dfM)
df_b = CBreturn.data_cleaning(df_merge)
df_minus = CBreturn.minus_rf(df_b)

end_date = datetime(2012, 12, 31)
end_now = datetime(2023, 12, 31)
df1 = CBreturn.replicate_columns(df_minus, end_date)
df2 = CBreturn.replicate_columns(df_minus, end_now)

df_expected = pd.read_csv(f'{DATA_DIR}/manual/He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv')

## Suppress scientific notation and limit to 3 decimal places
# Sets display, but doesn't affect formatting to LaTeX
pd.set_option('display.float_format', lambda x: '%.2f' % x)
# Sets format for printing to LaTeX
float_format_func = lambda x: '{:.2f}'.format(x)


def generate_summary_tables(df, name):
    # Generate Summary Statistics
    df_summary = df.describe()
    
    # Reset index and replace values in the index
    df_summary = df_summary.reset_index()
    df_summary['index'] = df_summary['index'].replace({'25%': '25\\%', '50%': '50\\%', '75%': '75\\%'})
    df_summary = df_summary.set_index('index')
    df_summary.index.name = None
    
    # Rename columns
    df_summary = df_summary.rename(columns={
        'US_bonds_11': 'US Bonds 11',
        'US_bonds_12': 'US Bonds 12',
        'US_bonds_13': 'US Bonds 13',
        'US_bonds_14': 'US Bonds 14',
        'US_bonds_15': 'US Bonds 15',
        'US_bonds_16': 'US Bonds 16',
        'US_bonds_17': 'US Bonds 17',
        'US_bonds_18': 'US Bonds 18',
        'US_bonds_19': 'US Bonds 19',
        'US_bonds_20': 'US Bonds 20',
    })

    # Convert DataFrame to LaTeX
    df_latex = df_summary.to_latex()

    # Split the df1_summary into two parts
    # Splitting logic
    latex_table_rows = df_latex.split('\n')
    column_headers = latex_table_rows[2].split('&')[1:]  # Skip the first element (group name)
    data_rows = [row.split('&') for row in latex_table_rows[4:-3]]  # Select only row data

    # Find the index of the last column for the first part
    last_column_first_part = ' US Bonds 15 '
    last_column_first_part_index = column_headers.index(last_column_first_part)

    # The first part
    part1_table = "\\begin{tabular}{l" + "r" * (last_column_first_part_index+1) + "}\n"
    part1_table += "\\toprule\n"
    part1_table += "group & " + " & ".join(column_headers[:last_column_first_part_index + 1]) + " \\\\\n"
    part1_table += "\\midrule\n"
    # Add data rows
    for row in data_rows:
        part1_table += " & ".join(row[:last_column_first_part_index + 2]) + " \\\\\n"
    part1_table += "\\bottomrule\n\\end{tabular}"


    # The second part
    part2_table = "\\begin{tabular}{l" + "r" * (len(column_headers) - last_column_first_part_index-1) + "}\n"
    part2_table += "\\toprule\n"
    part2_table += "group & " + " & ".join(column_headers[last_column_first_part_index + 1:]) + " \\\\\n"
    part2_table += "\\midrule\n"
    # Add data rows with the group name
    for row in data_rows:
        part2_table += row[0] + " & " + " & ".join(row[last_column_first_part_index+2:]) + " \\\\\n"
    part2_table += "\\bottomrule\n\\end{tabular}"


    # Write the first part of the LaTeX table to the specified file
    with open(f'{OUTPUT_DIR}/{name}_summary_table_part1.tex', 'w') as f:
        f.write(part1_table)
    # Write the second part of the LaTeX table to the specified file
    with open(f'{OUTPUT_DIR}/{name}_summary_table_part2.tex', 'w') as f:
        f.write(part2_table)

generate_summary_tables(df1, "2012")
generate_summary_tables(df2, "2023")


# Generate Summary Statistics (Year 1973-2023)
df2_summary = df2.drop('date', axis=1).describe()
df2_summary = pd.DataFrame(df2_summary).to_latex()
with open(f'{OUTPUT_DIR}/summary_table_now.tex', 'w') as f:
    f.write(df2_summary)




# graph
def generate_comparison_lineplot(df_expected, df):
    df_expected = df_expected[['yyyymm',
            'US_bonds_11', 'US_bonds_12',
            'US_bonds_13',	'US_bonds_14',
            'US_bonds_15',	'US_bonds_16',
            'US_bonds_17',	'US_bonds_18',
            'US_bonds_19',	'US_bonds_20',
        ]]

    df_raw = df[['date',
            'US_bonds_11', 'US_bonds_12',
            'US_bonds_13',	'US_bonds_14',
            'US_bonds_15',	'US_bonds_16',
            'US_bonds_17',	'US_bonds_18',
            'US_bonds_19',	'US_bonds_20',	
        ]]

    # Specify the time range
    start_date = datetime(1974, 1, 1)
    end_date = datetime(2011, 12, 31)

    # Filter the time range for df_expected
    df_expected['yyyymm'] = pd.to_datetime(df_expected['yyyymm'], format='%Y%m')
    subset_expected = df_expected[(df_expected['yyyymm'] >= start_date) & (df_expected['yyyymm'] <= end_date)] 

    # Filter the time range for df_raw
    df_raw['date'] = df_raw['date'].dt.to_timestamp()
    subset_actual = df_raw[(df_raw['date'] >= start_date) & (df_raw['date'] <= end_date)] 

    # Calculate and assign the mean to a new column
    subset_expected['mean'] = subset_expected.iloc[:, 1:].mean(axis=1)
    subset_actual['mean'] = subset_actual.iloc[:, 1:].mean(axis=1)    

    plt.plot(subset_actual['date'], subset_actual['mean'], linestyle='-', color='red')
    plt.plot(subset_expected['yyyymm'], subset_expected['mean'], linestyle='-', color='blue')
    plt.title('Comparison of US bond mean Over Time')
    plt.ylabel('US Bond Mean Values')
    plt.xlabel('Date')
    plt.grid(True)
    plt.legend()

    output_path = os.path.join(OUTPUT_DIR, 'comparison_lineplot.png')
    plt.savefig(output_path)

generate_comparison_lineplot(df_expected, df1)