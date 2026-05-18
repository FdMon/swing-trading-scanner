import pandas as pd
import numpy as np
from scanner.patterns import check_ascending_triangle

def _make_df(highs, lows, atr=None):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=len(highs))
    df = pd.DataFrame({
        "High": highs,
        "Low": lows,
        "ATR": atr if atr is not None else np.abs(np.diff(highs + lows)).tolist() + [0]
    }, index=dates)
    return df

def test_true_ascending_triangle():
    highs = [108, 110, 108, 110, 108, 110, 108, 110, 108, 110]
    lows = [90, 92, 95, 97, 100, 102, 105, 107, 110, 112]
    df = _make_df(highs, lows)
    ok, data = check_ascending_triangle(df, window=10, max_resistance_variance=0.015)
    assert ok, "Debe detectarse un triángulo ascendente real"
    assert data["resistance_level"] == 110
    assert len(data["peaks"]) >= 2
    assert len(data["valleys"]) >= 3

def test_false_not_a_triangle():
    np.random.seed(0)
    highs = np.random.uniform(80, 120, 15)
    lows = np.random.uniform(70, 110, 15)
    df = _make_df(highs, lows)
    ok, _ = check_ascending_triangle(df, window=15)
    assert not ok, "No debe detectarse triángulo en datos aleatorios"

def test_flat_resistance_fails():
    highs = [108, 112, 115, 110, 109, 111, 108, 115, 110, 112]
    lows = [90, 92, 95, 97, 100, 102, 105, 107, 110, 112]
    df = _make_df(highs, lows)
    ok, _ = check_ascending_triangle(df, window=10)
    assert not ok, "Resistencia no plana → no debe ser triángulo"
