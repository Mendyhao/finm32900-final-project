Replication of Nozawa, Yoshio's “What Drives the Cross‐Section of Credit Spreads?: A Variance Decomposition Approach.”
==================
### Julia Klauss, Joy Wu, Mengdi Hao, Yu-Ting Weng

# About this project

In this project, we replicate data and tables from Nozawa, Yoshio's “What Drives the Cross‐Section of Credit Spreads?: A Variance Decomposition Approach." In addition, we reproduce the data and tables with updated numbers until 2023/12/31. We replicate the corporate bond columns from the monthly test assets from He, Kelly, and Manela (2017).

## Data Collection

The panel data for corporate bond prices is constructed from three primary databases: Lehman Brothers Fixed Income Database, Mergent FISD/NAIC Database, and TRACE. The priority order for overlapping data is Lehman Brothers, TRACE, and Mergent FISD/NAIC. Lehman Brothers database covers from 1973/01 to 1998/03 and TRACE database covers from 2022/07 to 2023/12. The time gap between these two databases is filled by Mergent FISD/NAIC database.

Besides the above data sources on corporate bonds, the replication also involves using risk-free rate as the columns represent excess returns, which is calculated by corporate bond return minus a matching risk-free rate. Constant-maturity treasury yields are collected, according to Nozawa (2017), to calculate maturity-matching risk-free rate. There are 11 different maturities in the original treasury yields data: 1-month, 3-month, 6-month, 1-year, 2-year, 3-year, 5-year, 7-year, 10-year, 20-year, and 30-year. To find a matching risk-free rate for corporate bonds with different time-to-maturity, we conducted a cubic splines interpolation method to interpolate the original treasury yields. This interpolation process was done for every month during 1953/04 and 2024/01. The interpolation step is set to one month as our data frequency is monthly.After interpolation, we have monthly treasury yields from 1953/04 to 2024/01 for maturities from 1-month to 360-month.

## Data Processing

The merging process involves combining Lehman Brothers and TRACE data, and filling missing dates with Mergent FISD/NAIC.  As we utilize the WRDS Bond Return database, it's crucial to note that this source inherently includes monthly bond returns that account for defaults. We do not rely on Moody's Default Risk Service for complementing prices upon default. The dataset undergoes filtering to remove bonds with floating rates and non-callable options. Matching with synthetic Treasury bonds is performed to calculate excess returns and credit spreads. 

Data cleaning includes removing bonds with prices higher than matching Treasury bond prices and handling return observations showing significant bouncebacks. The final dataset is sorted into 10 columns based on yield spreads, each representing a U.S. corporate bond portfolio. This comprehensive process ensures a robust dataset for empirical analysis. 

# Quick Start

To quickest way to run code in this repo is to use the following steps. First, note that you must have TexLive installed on your computer and available in your path.
You can do this by downloading and installing it from here ([windows](https://tug.org/texlive/windows.html#install) and [mac](https://tug.org/mactex/mactex-download.html) installers).
Having installed LaTeX, open a terminal and navigate to the root directory of the project and create a conda environment using the following command:
```
conda create -n blank python=3.12
conda activate blank
```
and then install the dependencies with pip
```
pip install -r requirements.txt
```
You can then navigate to the `src` directory and then run 
```
doit
```
# General Directory Structure

 - The `assets` folder is used for things like hand-drawn figures or other pictures that were not generated from code. These things cannot be easily recreated if they are deleted.

 - The `output` folder, on the other hand, contains tables and figures that are generated from code. The entire folder should be able to be deleted, because the code can be run again, which would again generate all of the contents.

 - I'm using the `doit` Python module as a task runner. It works like `make` and the associated `Makefile`s. To rerun the code, install `doit` (https://pydoit.org/) and execute the command `doit` from the `src` directory. Note that doit is very flexible and can be used to run code commands from the command prompt, thus making it suitable for projects that use scripts written in multiple different programming languages.

 - I'm using the `.env` file as a container for absolute paths that are private to each collaborator in the project. You can also use it for private credentials, if needed. It should not be tracked in Git.

# Data and Output Storage

We pull the datasets and save them to a directory in the data folder called "pulled," which contains data that could hypothetically be deleted and recreated by rerunning the PyDoit command (the pulls are in the dodo.py file). Our manually-created data is stored in the data/manual folder.

Output is stored in the "output" directory. This includes our tables, charts, and rendered notebooks.

# Dependencies and Virtual Environments

## Working with `pip` requirements

`conda` allows for a lot of flexibility, but can often be slow. `pip`, however, is fast for what it does.  You can install the requirements for this project using the `requirements.txt` file specified here. Do this with the following command:
```
pip install -r requirements.txt
```

The requirements file can be created like this:
```
pip list --format=freeze
```

## Working with `conda` environments

The dependencies used in this environment (along with many other environments commonly used in data science) are stored in the conda environment called `blank` which is saved in the file called `environment.yml`. To create the environment from the file (as a prerequisite to loading the environment), use the following command:

```
conda env create -f environment.yml
```

Now, to load the environment, use

```
conda activate blank
```

Note that an environment file can be created with the following command:

```
conda env export > environment.yml
```

However, it's often preferable to create an environment file manually, as was done with the file in this project.

Also, these dependencies are also saved in `requirements.txt` for those that would rather use pip. Also, GitHub actions work better with pip, so it's nice to also have the dependencies listed here. This file is created with the following command:

```
pip freeze > requirements.txt
```

### Alternative Quickstart using Conda
Another way to  run code in this repo is to use the following steps.
First, open a terminal and navigate to the root directory of the project and create a conda environment using the following command:
```
conda env create -f environment.yml
```
Now, load the environment with
```
conda activate blank
```
Now, navigate to the directory called `src`
and run
```
doit
```
That should be it!



**Other helpful `conda` commands**

- Create conda environment from file: `conda env create -f environment.yml`
- Activate environment for this project: `conda activate blank`
- Remove conda environment: `conda remove --name myenv --all`
- Create blank conda environment: `conda create --name myenv --no-default-packages`
- Create blank conda environment with different version of Python: `conda create --name myenv --no-default-packages python` Note that the addition of "python" will install the most up-to-date version of Python. Without this, it may use the system version of Python, which will likely have some packages installed already.

## `mamba` and `conda` performance issues

Since `conda` has so many performance issues, it's recommended to use `mamba` instead. I recommend installing the `miniforge` distribution. See here: https://github.com/conda-forge/miniforge
