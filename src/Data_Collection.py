import os
from pathlib import Path

# Derive current working directory
current_dir = Path(os.getcwd())

# If current working directory is not 'src', update it
if current_dir.stem != 'src':
    src_directory = current_dir / 'src'
    os.chdir(src_directory)

import config
from pathlib import Path
OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
WRDS_USERNAME = config.WRDS_USERNAME

import wrds

# Connect to WRDS
db = wrds.Connection(wrds_username=WRDS_USERNAME)

# Collect TRACE data
sql_query_T = """select date,cusip,price_l5m,coupon,yield
                        from wrdsapps.bondret 
                        """
df_T = db.raw_sql(sql_query_T)
df_T.to_csv(DATA_DIR / "TRACE.csv", index = False)

# Collect Mergent data
sql_query_M = """select complete_cusip,flat_price,accrued_interest,trans_date 
                        from fisd.naic_bond_transactions 
                        """
df_M = db.raw_sql(sql_query_M)
df_M.to_csv(DATA_DIR / "Mergent.csv", index = False)