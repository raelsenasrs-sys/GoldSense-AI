import numpy as np
import pandas as pd

class MarketAnalystBrain1:
    """
    Brain 1: Market Analyst for GoldSense AI (XAUUSD Scalper).
    Evaluates trend, structure, liquidity, volatility, and session data.
    """
    def __init__(self, symbol="XAUUSD"):
        self.symbol = symbol

    def analyze_trend(self, df_lower: pd.DataFrame, df_higher: pd.DataFrame) -> dict:
        """Evaluates multi-timeframe trend using EMAs and price action."""
        # Assuming df contains 'close' prices and EMA calculations
        htf_ema_fast = df_higher['close'].ewm(span=20, adjust=False).mean().iloc[-1]
        htf_ema_slow = df_higher['close'].ewm(span=50, adjust=False).mean().iloc[-1]
        
        ltf_ema_fast = df_lower['close'].ewm(span=9, adjust=False).mean().iloc[-1]
        ltf_ema_slow = df_lower['close'].ewm(span=21, adjust=False).mean().iloc[-1]

        htf_trend = "BULLISH" if htf_ema_fast > htf_ema_slow else "BEARISH"
        ltf_trend = "BULLISH" if ltf_ema_fast > ltf_ema_slow else "BEARISH"

        return {
            "htf_trend": htf_trend,
            "ltf_trend": ltf_trend,
            "alignment": htf_trend == ltf_trend
        }

    def detect_market_structure(self, df: pd.DataFrame) -> str:
        """Identifies market structure phases: Trend, Range, or Consolidation."""
        highs = df['high'].rolling(window=5).max()
        lows = df['low'].rolling(window=5).min()
        
        # Simplified structure detection based on recent swing points
        recent_highs = df['high'].iloc[-10:].values
        recent_lows = df['low'].iloc[-10:].values

        if recent_highs[-1] > recent_highs[-3] and recent_lows[-1] > recent_lows[-3]:
            return "BULLISH_TREND"
        elif recent_highs[-1] < recent_highs[-3] and recent_lows[-1] < recent_lows[-3]:
            return "BEARISH_TREND"
        else:
            return "CONSOLIDATION_RANGE"

    def calculate_volatility(self, df: pd.DataFrame, period=14) -> dict:
        """Measures ATR and current spread validity for XAUUSD."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        
        current_spread = 0.15 # Mock live feed spread variable for XAUUSD in pips/points
        max_allowable_spread = 0.30

        return {
            "atr": round(atr, 2),
            "current_spread": current_spread,
            "volatility_acceptable": current_spread <= max_allowable_spread
        }

    def scan_liquidity_zones(self, df: pd.DataFrame) -> list:
        """Identifies key liquidity pools and potential Order Blocks / FVGs."""
        zones = []
        # Detection logic for equal highs/lows or institutional order blocks
        recent_resistance = df['high'].iloc[-20:].max()
        recent_support = df['low'].iloc[-20:].min()
        
        zones.append({"type": "RESISTANCE_LIQUIDITY", "level": recent_resistance})
        zones.append({"type": "SUPPORT_LIQUIDITY", "level": recent_support})
        return zones

    def run_analysis(self, df_ltf: pd.DataFrame, df_htf: pd.DataFrame) -> dict:
        """Compiles Brain 1 intelligence report for Brain 2 (Risk Manager)."""
        trend_data = self.analyze_trend(df_ltf, df_htf)
        structure = self.detect_market_structure(df_ltf)
        volatility = self.calculate_volatility(df_ltf)
        liquidity = self.scan_liquidity_zones(df_ltf)

        return {
            "status": "SUCCESS",
            "market_phase": structure,
            "trend_alignment": trend_data,
            "volatility_metrics": volatility,
            "liquidity_zones": liquidity
        }