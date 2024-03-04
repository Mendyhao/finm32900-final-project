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
OUTPUT_DIR = Path(config.OUTPUT_DIR)

# Import Coporate Bond Return Data
dfL = CBreturn.combine_Lehman()
dfT = CBreturn.read_trace()
dfM = CBreturn.read_mergent()
df_merge = CBreturn.merge_and_fillna(dfL, dfT, dfM)
df_b = CBreturn.data_cleaning(df_merge)

end_date = datetime(2012, 12, 31)
end_now = datetime(2023, 12, 31)
df1 = CBreturn.replicate_columns(df_b, end_date)
df2 = CBreturn.replicate_columns(df_b, end_now)



# Generate Summary Statistics
df1_summary = df1.drop('date', axis=1).describe()
df1_summary = pd.DataFrame(df1_summary).to_latex()
# Write the LaTeX table to the specified file
with open(f'{OUTPUT_DIR}/summary_table_2012.tex', 'w') as f:
    f.write(df1_summary)



df2_summary = df2.drop('date', axis=1).describe()
df2_summary = pd.DataFrame(df2_summary).to_latex()
with open(f'{OUTPUT_DIR}/summary_table_now.tex', 'w') as f:
    f.write(df2_summary)
