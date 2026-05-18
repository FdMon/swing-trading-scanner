import pandas as pd
import numpy as np
from typing import Tuple


def _find_local_maxima(series: np.ndarray, n: int = 3) -> list:
    """
    Encuentra máximos locales (picos) usando ventana de vecindad N a cada lado.
    Retorna lista de índices dentro del array.
    """
    peaks = []
    for i in range(n, len(series) - n):
        window_left = series[i - n:i]
        window_right = series[i + 1:i + n + 1]
        if series[i] > max(window_left) and series[i] > max(window_right):
            peaks.append(i)
    return peaks


def _find_local_minima(series: np.ndarray, n: int = 3) -> list:
    """
    Encuentra mínimos locales (valles) usando ventana de vecindad N a cada lado.
    Retorna lista de índices dentro del array.
    """
    valleys = []
    for i in range(n, len(series) - n):
        window_left = series[i - n:i]
        window_right = series[i + 1:i + n + 1]
        if series[i] < min(window_left) and series[i] < min(window_right):
            valleys.append(i)
    return valleys


def check_ascending_triangle(df: pd.DataFrame, window: int = 90, max_resistance_variance: float = 0.0075) -> Tuple[bool, dict]:
    """
    Detector de Triángulos Alcistas según especificación técnica de 90 días.

    FASE 1: Segmentación
      - Bloque Tendencia Previa: V1..V30 (primeras 30 velas)
      - Bloque Formación: V31..V90 (últimas 60 velas)

    FASE 2: Extracción de Pivotes (Fractales) con N=3

    FASE 3: 5 Reglas de validación
      R1: Tendencia previa alcista (≥5%)
      R2: Resistencia horizontal (≥2 picos, diferencia ≤0.75%)
      R3: Soporte ascendente (≥2 valles, V2 > V1 en ≥1.5%)
      R4: Compresión geométrica (D_fin ≤ 50% de D_ini)
      R5: Contracción de volumen

    FASE 4: Parámetros de salida (entry, stop_loss, take_profit)
    """
    if len(df) < window:
        return False, {}

    # ── FASE 1: Segmentación ──
    full_window = df.iloc[-window:]
    trend_block = full_window.iloc[:30]      # V1..V30
    formation_block = full_window.iloc[30:]  # V31..V90

    # ── FASE 3, REGLA 1: Tendencia Previa Alcista ──
    # Precio medio de cierre V1..V5 vs V25..V30
    avg_start = trend_block['Close'].iloc[:5].mean()
    avg_end = trend_block['Close'].iloc[-6:].mean()  # V25..V30

    pct_change = (avg_end - avg_start) / avg_start
    if pct_change < 0.05:  # Mínimo +5%
        return False, {}

    # ── FASE 2: Extracción de Pivotes en Bloque de Formación ──
    highs = formation_block['High'].values
    lows = formation_block['Low'].values

    peak_indices = _find_local_maxima(highs, n=3)
    valley_indices = _find_local_minima(lows, n=3)

    # ── REGLA 2: Resistencia Horizontal Estricta ──
    # Necesitamos al menos 2 picos
    if len(peak_indices) < 2:
        return False, {}

    peak_prices = highs[peak_indices]

    # Encontrar los 2 picos más altos
    sorted_peak_indices = sorted(range(len(peak_prices)), key=lambda i: peak_prices[i], reverse=True)
    top_two_idx = sorted(sorted_peak_indices[:2])  # Ordenados cronológicamente

    p1_price = peak_prices[top_two_idx[0]]
    p2_price = peak_prices[top_two_idx[1]]
    p1_pos = peak_indices[top_two_idx[0]]  # Posición dentro del bloque de formación
    p2_pos = peak_indices[top_two_idx[1]]

    # Tolerancia: diferencia ≤ 0.75%
    resistance_diff = abs(p1_price - p2_price) / max(p1_price, p2_price)
    if resistance_diff > max_resistance_variance:
        return False, {}

    # Línea de resistencia = promedio de los dos picos
    L_res = (p1_price + p2_price) / 2.0

    # ── REGLA 3: Soporte Ascendente Cuantificable ──
    if len(valley_indices) < 2:
        return False, {}

    valley_prices = lows[valley_indices]

    # Tomar los dos valles más prominentes (más bajos), ordenados cronológicamente
    # Buscamos valles donde V2 > V1 cronológicamente
    v1_idx = None
    v2_idx = None
    for i in range(len(valley_indices)):
        for j in range(i + 1, len(valley_indices)):
            vi_price = valley_prices[i]
            vj_price = valley_prices[j]
            # V2 debe ser cronológicamente después y estrictamente mayor en ≥1.5%
            pct_diff = (vj_price - vi_price) / vi_price
            if pct_diff >= 0.015:
                # Preferir el par con mayor separación temporal
                if v1_idx is None or (valley_indices[j] - valley_indices[i]) > (valley_indices[v2_idx] - valley_indices[v1_idx]):
                    v1_idx = i
                    v2_idx = j

    if v1_idx is None or v2_idx is None:
        return False, {}

    v1_price = valley_prices[v1_idx]
    v1_pos = valley_indices[v1_idx]
    v2_price = valley_prices[v2_idx]
    v2_pos = valley_indices[v2_idx]

    # Línea de soporte: recta que une V1 y V2
    # y = slope * x + intercept
    if v2_pos == v1_pos:
        return False, {}
    support_slope = (v2_price - v1_price) / (v2_pos - v1_pos)
    support_intercept = v1_price - support_slope * v1_pos

    # ── REGLA 4: Compresión Geométrica ──
    # D_ini = L_res - L_sup en la posición de V1
    L_sup_at_v1 = support_slope * v1_pos + support_intercept
    D_ini = L_res - L_sup_at_v1

    # D_fin = L_res - L_sup en la posición de la última vela (pos 59)
    last_pos = len(formation_block) - 1
    L_sup_at_end = support_slope * last_pos + support_intercept
    D_fin = L_res - L_sup_at_end

    # Altura para Proyección: Usar la altura máxima absoluta del bloque (desde la base)
    abs_min = formation_block['Low'].min()
    D_max = L_res - abs_min

    if D_ini <= 0 or D_fin <= 0 or D_max <= 0:
        return False, {}

    # D_fin debe ser ≤ 50% de D_ini
    compression_ratio = D_fin / D_ini
    if compression_ratio > 0.50:
        return False, {}

    # ── REGLA 5: Contracción de Volumen ──
    # Volumen medio V31..V45 (primeras 15 del bloque) vs V76..V90 (últimas 15)
    # Añadimos un margen de tolerancia del 5% para no descartar patrones perfectos por ruido o picos de volumen puntuales.
    vol_early = formation_block['Volume'].iloc[:15].mean()
    vol_late = formation_block['Volume'].iloc[-15:].mean()

    if vol_late >= vol_early * 1.05:
        return False, {}

    # ── REGLA 6: Precio actual DENTRO del triángulo ──
    # El cierre actual debe estar POR ENCIMA de la línea de soporte proyectada
    # y POR DEBAJO (o muy cerca) de la resistencia
    current_close = float(formation_block['Close'].iloc[-1])
    L_sup_current = support_slope * last_pos + support_intercept

    # Precio debe estar por encima del soporte
    if current_close < L_sup_current:
        return False, {}

    # Precio debe estar cerca de la resistencia (dentro del triángulo, no haberse desplomado)
    # Máximo un 5% por debajo de la resistencia
    if current_close < L_res * 0.95:
        return False, {}

    # Precio NO debe estar muy por encima de la resistencia (ya habría roto, no es setup)
    # Máximo 1.5% por encima (tolerancia para mecha del día)
    if current_close > L_res * 1.015:
        return False, {}

    # ═══════════════════════════════════════════════════
    # ── FASE 4: Parámetros de Salida ──
    # ═══════════════════════════════════════════════════
    atr_value = df['ATR'].iloc[-1] if 'ATR' in df.columns else (df['High'].iloc[-1] - df['Low'].iloc[-1])

    entry_price = round(float(L_res + 0.001 * atr_value), 2)
    # Take Profit: Resistencia + Altura Máxima (D_max)
    stop_loss = round(float(v2_price), 2)
    take_profit = round(float(L_res + D_max), 2)

    pattern_data = {
        'resistance_level': round(float(L_res), 2),
        'support_slope': round(float(support_slope), 4),
        'peaks': [round(float(p1_price), 2), round(float(p2_price), 2)],
        'valleys': [round(float(v1_price), 2), round(float(v2_price), 2)],
        'is_compressing': True,
        'compression_ratio': round(float(compression_ratio), 2),
        'prior_trend_pct': round(float(pct_change * 100), 2),
        'volume_contraction_pct': round(float((1 - vol_late / vol_early) * 100), 2),
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'D_ini': round(float(D_ini), 2),
        'D_fin': round(float(D_fin), 2),
    }

    return True, pattern_data


def check_volume_contraction(df: pd.DataFrame, window: int = 10) -> bool:
    """
    Checks if volume is generally contracting during the consolidation.
    """
    if len(df) < window:
        return False

    recent_vol = df['Volume'].iloc[-window:]

    # Compare average volume of last 5 days to previous 5 days
    half = window // 2
    vol_first_half = recent_vol.iloc[:half].mean()
    vol_second_half = recent_vol.iloc[half:].mean()

    return vol_second_half < vol_first_half
