import os
import json
from datetime import datetime
import pandas as pd

from data_loader import get_universe, update_historical_data, get_cached_ticker_data
from indicators import calculate_indicators
from patterns import check_ascending_triangle, check_volume_contraction
from scoring import calculate_score

import math
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_jsonbin_favorites(bin_id, api_key):
    if not bin_id:
        return []
    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    headers = {}
    if api_key:
        headers["X-Access-Key"] = api_key
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            record = data.get("record", {})
            return record.get("favorites", [])
    except Exception as e:
        print(f"Error fetching favorites from JSONBin: {e}")
    return []

def process_ticker(ticker, universe_dict, df_all, force_include=False):
    """Processes a single stock symbol using pre-loaded Parquet data."""
    try:
        # Load from Parquet cache (no network call)
        df = get_cached_ticker_data(ticker, df_all)
        if df is None or len(df) < 200:
            return None

        # Clean NaN price rows
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        if len(df) < 90:
            return None

        # Calculate Indicators
        df = calculate_indicators(df)

        # Detect Patterns
        is_triangle, pattern_data = check_ascending_triangle(df, window=90)
        has_vol_contraction = check_volume_contraction(df, window=10)

        if is_triangle or force_include:
            # Calculate Score
            score_data = calculate_score(df, pattern_data, has_vol_contraction)

            # Filter by Score Rule (>= 50)
            if score_data['total_score'] >= 50 or force_include:
                latest = df.iloc[-1]

                if math.isnan(latest['Close']):
                    return None

                ema_alignment = bool(latest['Close'] > latest['EMA20'] > latest['EMA50'])

                # Last 90 days for mini chart
                recent_df = df.iloc[-90:]
                history = []
                for idx, row in recent_df.iterrows():
                    history.append({
                        "date": str(idx.date() if hasattr(idx, 'date') else idx),
                        "open": round(float(row['Open']), 2),
                        "high": round(float(row['High']), 2),
                        "low": round(float(row['Low']), 2),
                        "close": round(float(row['Close']), 2),
                        "volume": int(row['Volume'])
                    })

                indices = universe_dict.get(ticker, [])
                index_str = " / ".join(indices) if indices else "Unknown"

                opp = {
                    "ticker": ticker,
                    "index": index_str,
                    "score": score_data['total_score'],
                    "pattern": "ascending_triangle",
                    "price": round(float(latest['Close']), 2),
                    "ema_alignment": ema_alignment,
                    "volume_score": score_data['volume_score'],
                    "atr_compression": round(float(latest.get('BBW', 0)), 2),
                    "breakdown": score_data,
                    "date": str(latest.name.date() if hasattr(latest.name, 'date') else datetime.now().date()),
                    "history": history,
                    "entry_price": pattern_data.get('entry_price'),
                    "stop_loss": pattern_data.get('stop_loss'),
                    "take_profit": pattern_data.get('take_profit'),
                    "resistance_level": pattern_data.get('resistance_level'),
                    "compression_ratio": pattern_data.get('compression_ratio'),
                    "prior_trend_pct": pattern_data.get('prior_trend_pct'),
                    "volume_contraction_pct": pattern_data.get('volume_contraction_pct')
                }
                return opp
    except Exception:
        pass
    return None

def run_scanner():
    print(f"Starting Scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load favorites from JSONBin
    bin_id = os.environ.get("JSONBIN_BIN_ID")
    api_key = os.environ.get("JSONBIN_API_KEY")
    favorites_list = []
    if bin_id:
        print("Fetching favorites from JSONBin...")
        favorites_list = get_jsonbin_favorites(bin_id, api_key)

    favorite_tickers = [f["ticker"] for f in favorites_list if "ticker" in f]
    print(f"Loaded {len(favorite_tickers)} favorites.")

    # 1. Get Universe
    universe_dict = get_universe(
        include_sp500=True, include_ndx=True, include_dow=True, include_sp400=True,
        include_eurostoxx=True, include_dax=True, include_cac=True,
        include_ibex=True, include_ftse=True
    )
    tickers = list(universe_dict.keys())

    # 2. Batch download and update Parquet cache (fast: batches of 250)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, 'data')
    print(f"Updating historical data for {len(tickers)} tickers...")
    update_historical_data(tickers, data_dir=data_dir)

    # 3. Load the full Parquet into memory once (all reads come from here)
    parquet_path = os.path.join(data_dir, 'history.parquet')
    df_all = None
    if os.path.exists(parquet_path):
        try:
            df_all = pd.read_parquet(parquet_path)
            print(f"Loaded Parquet: {len(df_all)} rows for {df_all['Ticker'].nunique()} tickers.")
        except Exception as e:
            print(f"Error loading Parquet for scanning: {e}")

    if df_all is None:
        print("ERROR: No historical data available. Aborting.")
        return

    # 4. Process all tickers in parallel (pure computation, no network calls)
    opportunities = []
    max_workers = 32  # More workers since no I/O bottleneck
    print(f"Scanning {len(tickers)} tickers in parallel using {max_workers} threads...")

    completed_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_ticker, ticker, universe_dict, df_all): ticker
            for ticker in tickers
        }
        for future in as_completed(futures):
            ticker = futures[future]
            completed_count += 1
            print(f"[{completed_count}/{len(tickers)}] Scanned {ticker}...", end="\r")
            try:
                opp = future.result()
                if opp is not None:
                    opportunities.append(opp)
            except Exception:
                pass

    print("\nScan Complete!")
    print(f"Found {len(opportunities)} opportunities >= 50 score.")

    # 5. Ensure all favorites are in results (even if not in scanner today)
    scanned_tickers = {opp["ticker"] for opp in opportunities}
    missing_favorites = [t for t in favorite_tickers if t not in scanned_tickers]

    if missing_favorites:
        print(f"Force-including {len(missing_favorites)} missing favorites...")
        with ThreadPoolExecutor(max_workers=min(max_workers, len(missing_favorites))) as executor:
            futures = {
                executor.submit(process_ticker, ticker, universe_dict, df_all, True): ticker
                for ticker in missing_favorites
            }
            for future in as_completed(futures):
                try:
                    opp = future.result()
                    if opp is not None:
                        opportunities.append(opp)
                except Exception:
                    pass

    # 6. Save JSON
    dashboard_data_dir = os.path.join(base_dir, 'dashboard', 'public', 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(dashboard_data_dir, exist_ok=True)

    output_file = os.path.join(data_dir, 'opportunities.json')
    dashboard_file = os.path.join(dashboard_data_dir, 'opportunities.json')

    opportunities = sorted(opportunities, key=lambda x: x['score'], reverse=True)

    def json_clean(obj):
        """Recursively replace NaN/Inf with None for JSON compatibility."""
        if isinstance(obj, dict):
            return {k: json_clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [json_clean(x) for x in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
        return obj

    clean_opportunities = json_clean(opportunities)

    with open(output_file, 'w') as f:
        json.dump(clean_opportunities, f, indent=2)

    with open(dashboard_file, 'w') as f:
        json.dump(clean_opportunities, f, indent=2)

    print(f"Results saved to {output_file} and {dashboard_file}")

    # 7. Alertas (Placeholder, we parked Telegram for now)
    # from alerts.telegram import send_alert
    # for opp in opportunities:
    #     send_alert(opp)

if __name__ == "__main__":
    run_scanner()
