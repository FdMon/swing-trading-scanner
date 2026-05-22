import yfinance as yf
import pandas as pd
from typing import List, Optional
import time
import requests
from bs4 import BeautifulSoup
import io

def get_sp500_tickers() -> List[str]:
    """
    Fetches the current S&P 500 tickers from Wikipedia.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Wrap the html string in io.StringIO to avoid deprecation warning
        table = pd.read_html(io.StringIO(response.text))
        df = table[0]
        tickers = df['Symbol'].tolist()
        # Clean tickers (e.g. replace dots with hyphens for yfinance)
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        # Fallback list if wikipedia fails
        return ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'META', 'GOOGL', 'TSLA']

def get_nasdaq100_tickers() -> List[str]:
    """
    Fetches Nasdaq 100 tickers.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Wrap the html string in io.StringIO to avoid deprecation warning
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Ticker' in tbl.columns:
                return tbl['Ticker'].tolist()
        print("Could not find Ticker column in Nasdaq-100 tables. Using fallback.")
        return ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'AVGO', 'TSLA', 'GOOGL', 'GOOG', 'COST']
    except Exception as e:
        print(f"Error fetching Nasdaq 100 tickers: {e}")
        return ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META']

def get_dow_jones_tickers() -> List[str]:
    """
    Fetches the current Dow Jones Industrial Average tickers from Wikipedia.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Wrap the html string in io.StringIO to avoid deprecation warning
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Symbol' in tbl.columns:
                tickers = tbl['Symbol'].tolist()
                # Clean tickers (e.g. replace dots with hyphens for yfinance)
                tickers = [str(ticker).replace('.', '-') for ticker in tickers]
                return tickers
        print("Could not find Symbol column in Dow Jones tables. Using fallback.")
        return ['AAPL', 'MSFT', 'V', 'JPM', 'UNH', 'GS', 'HD', 'MCD', 'BA', 'CAT']
    except Exception as e:
        print(f"Error fetching Dow Jones tickers: {e}")
        return ['AAPL', 'MSFT', 'V', 'JPM', 'UNH']

def get_sp400_tickers() -> List[str]:
    """
    Fetches S&P MidCap 400 tickers from Wikipedia.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Symbol' in tbl.columns:
                tickers = tbl['Symbol'].tolist()
                tickers = [str(ticker).replace('.', '-') for ticker in tickers]
                return tickers
            elif 'Ticker symbol' in tbl.columns:
                tickers = tbl['Ticker symbol'].tolist()
                tickers = [str(ticker).replace('.', '-') for ticker in tickers]
                return tickers
        print("Could not find Symbol column in S&P 400 tables. Using fallback.")
        return []
    except Exception as e:
        print(f"Error fetching S&P 400 tickers: {e}")
        return []

        return []

def get_eurostoxx50_tickers() -> List[str]:
    try:
        url = 'https://en.wikipedia.org/wiki/EURO_STOXX_50'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Ticker' in tbl.columns:
                return tbl['Ticker'].tolist()
        return []
    except Exception as e:
        print(f"Error fetching EURO STOXX 50: {e}")
        return []

def _add_suffix_if_missing(ticker: str, suffix: str) -> str:
    ticker = str(ticker).strip()
    if not ticker.endswith(suffix):
        # Remove any other dot-suffix if present? No, let's just check if it already has a dot
        if '.' in ticker and not ticker.endswith(suffix):
             # If it has a different suffix, maybe keep it? 
             # For indices like DAX, they should all be .DE
             ticker = ticker.split('.')[0]
        return f"{ticker}{suffix}"
    return ticker

def get_dax_tickers() -> List[str]:
    try:
        url = 'https://en.wikipedia.org/wiki/DAX'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Ticker' in tbl.columns:
                return [_add_suffix_if_missing(t, ".DE") for t in tbl['Ticker'].tolist()]
        return []
    except Exception as e:
        print(f"Error fetching DAX: {e}")
        return []

def get_cac_tickers() -> List[str]:
    try:
        url = 'https://en.wikipedia.org/wiki/CAC_40'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Ticker' in tbl.columns:
                return [_add_suffix_if_missing(t, ".PA") for t in tbl['Ticker'].tolist()]
        return []
    except Exception as e:
        print(f"Error fetching CAC 40: {e}")
        return []

def get_ibex_tickers() -> List[str]:
    try:
        url = 'https://en.wikipedia.org/wiki/IBEX_35'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            if 'Ticker' in tbl.columns:
                return [_add_suffix_if_missing(t, ".MC") for t in tbl['Ticker'].tolist()]
        return []
    except Exception as e:
        print(f"Error fetching IBEX 35: {e}")
        return []

def get_ftse_tickers() -> List[str]:
    try:
        url = 'https://en.wikipedia.org/wiki/FTSE_100_Index'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        table = pd.read_html(io.StringIO(response.text))
        for tbl in table:
            col = 'EPIC' if 'EPIC' in tbl.columns else 'Ticker'
            if col in tbl.columns:
                return [_add_suffix_if_missing(t, ".L") for t in tbl[col].tolist()]
        return []
    except Exception as e:
        print(f"Error fetching FTSE 100: {e}")
        return []

def get_universe(include_sp500: bool = True, include_ndx: bool = True, include_dow: bool = True, include_sp400: bool = True, 
                 include_eurostoxx: bool = True, include_dax: bool = True, include_cac: bool = True, 
                 include_ibex: bool = True, include_ftse: bool = True) -> dict:
    """
    Combines the requested universes and maps them to their indices.
    Returns a dict: { 'AAPL': ['S&P 500', 'Nasdaq 100', 'Dow Jones'], ... }
    """
    universe = {}
    if include_sp500:
        for ticker in get_sp500_tickers():
            universe.setdefault(ticker, []).append("S&P 500")
    if include_ndx:
        for ticker in get_nasdaq100_tickers():
            universe.setdefault(ticker, []).append("Nasdaq 100")
    if include_dow:
        for ticker in get_dow_jones_tickers():
            universe.setdefault(ticker, []).append("Dow Jones")
    if include_sp400:
        for ticker in get_sp400_tickers():
            universe.setdefault(ticker, []).append("S&P MidCap 400")
    
    if include_eurostoxx:
        for ticker in get_eurostoxx50_tickers():
            universe.setdefault(ticker, []).append("EURO STOXX 50")
    if include_dax:
        for ticker in get_dax_tickers():
            universe.setdefault(ticker, []).append("DAX 40")
    if include_cac:
        for ticker in get_cac_tickers():
            universe.setdefault(ticker, []).append("CAC 40")
    if include_ibex:
        for ticker in get_ibex_tickers():
            universe.setdefault(ticker, []).append("IBEX 35")
    if include_ftse:
        for ticker in get_ftse_tickers():
            universe.setdefault(ticker, []).append("FTSE 100")
    
    return universe

import os
import math
from datetime import datetime, timedelta

def update_historical_data(tickers: List[str], data_dir: str = 'data'):
    """
    Downloads historical data using batch processing and Parquet cache.
    On Sundays, ignores cache and forces a full 1y download for dividends/splits.
    """
    parquet_path = os.path.join(data_dir, 'history.parquet')
    os.makedirs(data_dir, exist_ok=True)
    
    today = datetime.now()
    is_sunday = today.weekday() == 6
    
    df_cached = None
    if not is_sunday and os.path.exists(parquet_path):
        try:
            df_cached = pd.read_parquet(parquet_path)
            print(f"Loaded {len(df_cached)} rows from Parquet cache.")
        except Exception as e:
            print(f"Error loading Parquet: {e}")
            df_cached = None

    start_date = None
    period = '1y'
    already_up_to_date = False
    
    if df_cached is not None and not df_cached.empty and 'Date' in df_cached.columns:
        last_date = df_cached['Date'].max()
        if hasattr(last_date, 'tzinfo') and last_date.tzinfo is not None:
            last_date = last_date.tz_localize(None)

        next_date = last_date + timedelta(days=1)
        
        # If the next date to fetch is today or in the future, the cache is already up to date
        if next_date.date() >= today.date():
            print(f"Cache is already up to date (last date: {last_date.date()}). Skipping download.")
            already_up_to_date = True
        else:
            start_date = next_date.strftime('%Y-%m-%d')
            period = None
            print(f"Incremental update. Fetching from {start_date} for {len(tickers)} tickers.")
    else:
        print(f"Full refresh. Fetching 1y data for {len(tickers)} tickers.")
        df_cached = pd.DataFrame()

    if already_up_to_date:
        return  # Nothing to download, cache is fresh


    chunk_size = 250
    all_new_data = []
    
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i+chunk_size]
        print(f"Fetching chunk {i//chunk_size + 1}/{math.ceil(len(tickers)/chunk_size)}...")
        try:
            kwargs = {'progress': False, 'group_by': 'ticker'}
            if start_date:
                kwargs['start'] = start_date
            else:
                kwargs['period'] = period
                
            data = yf.download(chunk, **kwargs)
            if data.empty:
                continue
                
            if len(chunk) == 1:
                df = data.copy()
                df['Ticker'] = chunk[0]
                all_new_data.append(df.reset_index())
            else:
                for ticker in chunk:
                    if ticker in data.columns.get_level_values(0):
                        df = data[ticker].dropna(how='all').copy()
                        if not df.empty:
                            df['Ticker'] = ticker
                            all_new_data.append(df.reset_index())
        except Exception as e:
            print(f"Error fetching chunk: {e}")
            
    if all_new_data:
        new_df = pd.concat(all_new_data, ignore_index=True)
        # Format columns: Date, Open, High, Low, Close, Volume, Ticker
        # Sometimes yf returns 'Price' as level 1, dropping multiindex if flat
        if isinstance(new_df.columns, pd.MultiIndex):
            new_df.columns = [c[0] for c in new_df.columns]
            
        cols_map = {c: c.capitalize() for c in new_df.columns if isinstance(c, str)}
        new_df.rename(columns=cols_map, inplace=True)
        
        if 'Date' in new_df.columns and hasattr(new_df['Date'].dtype, 'tz') and new_df['Date'].dtype.tz is not None:
            new_df['Date'] = new_df['Date'].dt.tz_localize(None)
            
        if not df_cached.empty:
            final_df = pd.concat([df_cached, new_df], ignore_index=True)
            final_df.drop_duplicates(subset=['Date', 'Ticker'], keep='last', inplace=True)
        else:
            final_df = new_df
            
        try:
            final_df.to_parquet(parquet_path, engine='fastparquet')
            print(f"Saved {len(final_df)} rows to {parquet_path}")
        except Exception as e:
            print(f"Failed to save Parquet: {e}")
            # Try falling back to pyarrow
            try:
                final_df.to_parquet(parquet_path, engine='pyarrow')
                print(f"Saved {len(final_df)} rows to {parquet_path} (via pyarrow)")
            except Exception as e2:
                print(f"Failed to save Parquet via pyarrow: {e2}")
    else:
        print("No new data fetched.")

def get_cached_ticker_data(ticker: str, df_cached: pd.DataFrame) -> Optional[pd.DataFrame]:
    if df_cached is None or df_cached.empty:
        return None
    ticker_df = df_cached[df_cached['Ticker'] == ticker].copy()
    if ticker_df.empty:
        return None
    
    if 'Date' in ticker_df.columns:
        ticker_df.set_index('Date', inplace=True)
    ticker_df.sort_index(inplace=True)
    
    # Ensure standard columns are present
    for col in ['Open', 'High', 'Low', 'Close']:
        if col not in ticker_df.columns:
            return None
            
    return ticker_df

if __name__ == "__main__":
    universe = get_universe(include_sp500=True, include_ndx=False, include_dow=False, include_sp400=False, include_eurostoxx=False, include_dax=False, include_cac=False, include_ibex=False, include_ftse=False)
    tickers = list(universe.keys())[:10] # test small subset
    update_historical_data(tickers)
    
    df = pd.read_parquet('data/history.parquet')
    test_df = get_cached_ticker_data(tickers[0], df)
    print(test_df.tail() if test_df is not None else "No data")
