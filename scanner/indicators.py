import pandas as pd
import pandas_ta as ta

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical indicators using pandas-ta.
    """
    if df is None or df.empty:
        return df
        
    df = df.copy()
    
    # 1. Trend: EMAs
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=200, append=True)
    
    # 2. Momentum: RSI
    df.ta.rsi(length=14, append=True)
    
    # 3. Volatility: ATR and Bollinger Bands
    df.ta.atr(length=14, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    
    # Calculate Bollinger Band Width explicitly if not present 
    # (pandas-ta usually creates BBB_20_2.0 for bandwidth)
    bbw_col = [col for col in df.columns if 'BBB' in col]
    if bbw_col:
        df['BBW'] = df[bbw_col[0]]
    else:
        # Fallback manual calculation
        bbl_col = [col for col in df.columns if 'BBL' in col]
        bbu_col = [col for col in df.columns if 'BBU' in col]
        bbm_col = [col for col in df.columns if 'BBM' in col]
        if bbl_col and bbu_col and bbm_col:
             df['BBW'] = (df[bbu_col[0]] - df[bbl_col[0]]) / df[bbm_col[0]] * 100
             
    # Clean up column names for easier access later
    rename_map = {}
    for col in df.columns:
        if col.startswith('EMA_200'): rename_map[col] = 'EMA200'
        elif col.startswith('EMA_50'): rename_map[col] = 'EMA50'
        elif col.startswith('EMA_20'): rename_map[col] = 'EMA20'
        elif col.startswith('RSI_14'): rename_map[col] = 'RSI'
        elif col.startswith('ATR_14'): rename_map[col] = 'ATR'
        
    df.rename(columns=rename_map, inplace=True)
    
    return df
