Replication of Nozawa, Yoshio's “What Drives the Cross‐Section of Credit Spreads?: A Variance Decomposition Approach.”
==================
### Julia Klauss, Joy Wu, Mengdi Hao, Yu-Ting Weng

# About this project

In this project, we replicate data and tables from Nozawa, Yoshio's "What Drives the Cross‐Section of Credit Spreads?: A Variance Decomposition Approach." In addition, we reproduce the data and tables with updated numbers until 2023/12/31. We replicate the corporate bond columns from the monthly test assets from He, Kelly, and Manela (2017).

## Data Collection

The panel data for corporate bond prices is constructed from three primary databases: Lehman Brothers Fixed Income Database, Mergent FISD/NAIC Database, and TRACE. The priority order for overlapping data is Lehman Brothers, TRACE, and Mergent FISD/NAIC. Lehman Brothers database covers from 1973/01 to 1998/03 and TRACE database covers from 2022/07 to 2023/12. The time gap between these two databases is filled by Mergent FISD/NAIC database.

Besides the above data sources on corporate bonds, the replication also involves using risk-free rate as the columns represent excess returns, which is calculated by corporate bond return minus a matching risk-free rate. Constant-maturity treasury yields are collected, according to Nozawa (2017), to calculate maturity-matching risk-free rate. There are 11 different maturities in the original treasury yields data: 1-month, 3-month, 6-month, 1-year, 2-year, 3-year, 5-year, 7-year, 10-year, 20-year, and 30-year. To find a matching risk-free rate for corporate bonds with different time-to-maturity, we conducted a cubic splines interpolation method to interpolate the original treasury yields. This interpolation process was done for every month during 1953/04 and 2024/01. The interpolation step is set to one month as our data frequency is monthly.After interpolation, we have monthly treasury yields from 1953/04 to 2024/01 for maturities from 1-month to 360-month.

## Data Processing

The merging process involves combining Lehman Brothers and TRACE data, and filling missing dates with Mergent FISD/NAIC.  As we utilize the WRDS Bond Return database, it's crucial to note that this source inherently includes monthly bond returns that account for defaults. We do not rely on Moody's Default Risk Service for complementing prices upon default. The dataset undergoes filtering to remove bonds with floating rates and non-callable options. Matching with synthetic Treasury bonds is performed to calculate excess returns and credit spreads. 

Data cleaning includes removing bonds with prices higher than matching Treasury bond prices and handling return observations showing significant bouncebacks. The final dataset is sorted into 10 columns based on yield spreads, each representing a U.S. corporate bond portfolio. This comprehensive process ensures a robust dataset for empirical analysis.