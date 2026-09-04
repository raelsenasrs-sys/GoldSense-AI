import MetaTrader5 as mt5
import pandas as pd

class MT5Bridge:
    """
    Handles connection, data streaming, and order execution via MetaTrader 5.
    """
    def __init__(self, symbol="XAUUSD"):
        self.symbol = symbol

    def connect(self):
        """Initializes connection to the MT5 terminal."""
        if not mt5.initialize():
            print(f"MT5 Initialization Failed, error code = {mt5.last_error()}")
            return False
        
        # Ensure symbol is available in Market Watch
        if not mt5.symbol_select(self.symbol, True):
            print(f"Failed to select {self.symbol} in Market Watch.")
            return False
            
        print(f"Successfully connected to MetaTrader 5. Active Symbol: {self.symbol}")
        return True

    def fetch_live_rates(self, timeframe=mt5.TIMEFRAME_M1, num_bars=150) -> pd.DataFrame:
        """Fetches live historical candles straight from the MT5 terminal."""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_bars)
        if rates is None:
            print(f"Failed to fetch rates for {self.symbol}")
            return pd.DataFrame()

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        # Standardize column names to lowercase to match our Brains
        df.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'tick_volume': 'volume'}, inplace=True)
        return df

    def execute_order(self, order_type: str, lot_size: float, price: float, sl: float, tp: float):
        """Dispatches a market order (BUY or SELL) to MT5."""
        action_type = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
        point = mt5.symbol_info(self.symbol).point
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(lot_size),
            "type": action_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "GoldSense AI Scalp",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order execution failed, retcode={result.retcode}")
            return False
        
        print(f"Order successfully executed! Ticket ID: {result.order}")
        return True

    def disconnect(self):
        mt5.shutdown()