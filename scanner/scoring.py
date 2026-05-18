import pandas as pd

def calculate_score(df: pd.DataFrame, pattern_data: dict, has_volume_contraction: bool) -> dict:
    """
    Calculates the setup score (0-100) based on weights:
    - Trend (25%)
    - Pattern Quality (25%)
    - Volume (20%)
    - Volatility Compression (15%)
    - Relative Strength (15%) - *Simplified to RSI for MVP*
    """
    if df is None or df.empty or len(df) < 1:
        return {'total_score': 0}
        
    latest = df.iloc[-1]
    
    score_breakdown = {
        'trend_score': 0,
        'pattern_score': 0,
        'volume_score': 0,
        'volatility_score': 0,
        'rs_score': 0,
        'total_score': 0
    }
    
    # 1. Trend Background (25 points)
    # Check EMA alignment: Price > EMA20 > EMA50 > EMA200
    if 'EMA20' in latest and 'EMA50' in latest and 'EMA200' in latest:
        if latest['Close'] > latest['EMA20']:
            score_breakdown['trend_score'] += 10
        if latest['EMA20'] > latest['EMA50']:
            score_breakdown['trend_score'] += 10
        if latest['EMA50'] > latest['EMA200']:
            score_breakdown['trend_score'] += 5
            
    # 2. Pattern Quality (25 points)
    # For MVP, if pattern is detected we give base points, plus bonus if it's visually tight
    score_breakdown['pattern_score'] = 15 # Base for being an Ascending Triangle
    if pattern_data.get('is_compressing', False):
        score_breakdown['pattern_score'] += 10
        
    # 3. Volume Contraction (20 points)
    if has_volume_contraction:
        score_breakdown['volume_score'] = 20
        
    # 4. Volatility Compression (15 points)
    # Lower BBW (Bollinger Band Width) implies higher compression
    if 'BBW' in latest:
        # A BBW under 10% is usually quite compressed. We scale it.
        bbw = latest['BBW']
        if pd.notna(bbw):
            if bbw < 5:
                score_breakdown['volatility_score'] = 15
            elif bbw < 10:
                score_breakdown['volatility_score'] = 10
            elif bbw < 15:
                score_breakdown['volatility_score'] = 5
                
    # 5. Relative Strength / Momentum (15 points)
    # For MVP, we use RSI. Ideal breakout RSI is between 55 and 70 (bullish momentum but not overbought yet)
    if 'RSI' in latest:
        rsi = latest['RSI']
        if pd.notna(rsi):
            if 55 <= rsi <= 70:
                score_breakdown['rs_score'] = 15
            elif 50 <= rsi < 55 or 70 < rsi <= 75:
                score_breakdown['rs_score'] = 8
                
    score_breakdown['total_score'] = sum([
        score_breakdown['trend_score'],
        score_breakdown['pattern_score'],
        score_breakdown['volume_score'],
        score_breakdown['volatility_score'],
        score_breakdown['rs_score']
    ])
    
    return score_breakdown
