import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__)))

from data_loader import update_historical_data, get_cached_ticker_data, get_universe
import pandas as pd

uni = get_universe(include_sp500=True, include_ndx=False, include_dow=False,
                   include_sp400=False, include_eurostoxx=False, include_dax=False,
                   include_cac=False, include_ibex=False, include_ftse=False)
tickers = list(uni.keys())[:20]
print(f"Testing with {len(tickers)} tickers: {tickers[:5]}...")

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

# --- First run: full download ---
t0 = time.time()
update_historical_data(tickers, data_dir=data_dir)
t1 = time.time()
print(f"Full download time: {t1-t0:.1f}s")

df = pd.read_parquet(os.path.join(data_dir, 'history.parquet'))
print(f"Parquet loaded: {len(df)} rows, {df['Ticker'].nunique()} tickers")

# --- Second run: incremental (should be near-instant) ---
t2 = time.time()
update_historical_data(tickers, data_dir=data_dir)
t3 = time.time()
print(f"Incremental update time: {t3-t2:.1f}s")

# --- Test get_cached_ticker_data ---
df2 = pd.read_parquet(os.path.join(data_dir, 'history.parquet'))
sample_ticker = tickers[0]
ticker_df = get_cached_ticker_data(sample_ticker, df2)
if ticker_df is not None:
    print(f"Data for {sample_ticker}: {len(ticker_df)} rows, last date: {ticker_df.index[-1]}")
else:
    print(f"No data found for {sample_ticker}")
