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

def download_data(ticker: str, period: str = '1y', interval: str = '1d') -> Optional[pd.DataFrame]:
    """
    Downloads historical data for a given ticker.
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        
        # Flatten MultiIndex columns if present (yfinance sometimes does this)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        print(f"Error downloading data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test
    universe = get_universe()
    print(f"Universe size: {len(universe)} tickers")
    if universe:
        test_ticker = universe[0]
        print(f"Testing download for {test_ticker}")
        df = download_data(test_ticker)
        if df is not None:
            print(df.tail())
