"""
This file collects data from WRDS. There are two tables involved here: wrdsapps.bondret, fisd.naic_bond_transactions.
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
from pathlib import Path
OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
WRDS_USERNAME = config.WRDS_USERNAME

import wrds

def collect_trace():
    # Connect to WRDS
    db = wrds.Connection(wrds_username=WRDS_USERNAME)

    # Collect TRACE data
    sql_query_T = """select date,cusip,price_l5m,coupon,yield,maturity
                            from wrdsapps.bondret 
                            """
    df_T = db.raw_sql(sql_query_T)

    return df_T


# def collect_mergent():
#     # Connect to WRDS
#     db = wrds.Connection(wrds_username=WRDS_USERNAME)

#     # Collect Mergent data
#     sql_query_M = """select complete_cusip,flat_price,accrued_interest,trans_date 
#                             from fisd.naic_bond_transactions 
#                             """
#     df_M = db.raw_sql(sql_query_M)

#     return df_M



if __name__ == "__main__":
    
    # Call functions
    df_T = collect_trace()
    # df_M = collect_mergent()

    # Export output
    df_T.to_csv(DATA_DIR / "TRACE.csv", index = False)
    # df_M.to_csv(DATA_DIR / "Mergent.csv", index = False)