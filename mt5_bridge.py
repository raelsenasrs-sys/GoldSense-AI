import time
import MetaTrader5 as mt5
import pandas as pd
from supabase import create_client

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
try:
  supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
  print(f"Warning: Supabase client initialization failed: {e}")
  supabase = None

SYMBOL = "XAUUSD"
MAGIC_NUMBER = 234000


def initialize_mt5():
  if not mt5.initialize():
    print("MT5 initialization failed. Error:", mt5.last_error())
    if not mt5.initialize(
        path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    ):
      return False
  mt5.symbol_select(SYMBOL, True)
  return True


def ensure_connection():
  if not mt5.terminal_info() or not mt5.terminal_info().connected:
    print("MT5 connection lost. Attempting re-initialization...")
    return initialize_mt5()
  return True


def sync_telemetry():
  if supabase is None:
    return
  account_info = mt5.account_info()
  if account_info is None:
    return

  positions = mt5.positions_get(symbol=SYMBOL)
  open_trades_count = (
      len([p for p in positions if p.magic == MAGIC_NUMBER])
      if positions
      else 0
  )

  data = {
      "balance": account_info.balance,
      "equity": account_info.equity,
      "open_trades": open_trades_count,
      "status_message": "GoldSense Hardened Engine Active: Resilient Mode",
      "timestamp": pd.Timestamp.now().isoformat(),
  }
  try:
    supabase.table("trading_metrics").insert(data).execute()
  except Exception as e:
    # Fail gracefully so cloud errors never interrupt trade execution loops
    print(f"Cloud telemetry sync bypassed (network/db error): {e}")


def handle_order_result(result, action_name):
  if result is None:
    print(f"Error: {action_name} returned None response.")
    return False

  if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(
        f"Warning: {action_name} failed with retcode {result.retcode}:"
        f" {result.comment}"
    )
    return False
  else:
    print(f"Success: {action_name} executed. Ticket: {result.order}")
    return True


def check_breakout_entry():
  if not ensure_connection():
    return

  positions = mt5.positions_get(symbol=SYMBOL)
  active_positions = (
      [p for p in positions if p.magic == MAGIC_NUMBER] if positions else []
  )
  if len(active_positions) > 0:
    return

  rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 20)
  if rates is None or len(rates) < 20:
    return

  closes = [bar["close"] for bar in rates]
  highs = [bar["high"] for bar in rates[:-1]]
  lows = [bar["low"] for bar in rates[:-1]]

  resistance = max(highs)
  support = min(lows)
  current_price = closes[-1]

  symbol_info = mt5.symbol_info(SYMBOL)
  point = symbol_info.point
  tick = mt5.symbol_info_tick(SYMBOL)
  if not tick or not symbol_info:
    return

  if current_price > resistance:
    entry_price = tick.ask
    sl = entry_price - (300 * point)
    tp = entry_price + (600 * point)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": entry_price,
        "sl": float(sl),
        "tp": float(tp),
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "GoldSense Hardened Buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    handle_order_result(result, "Breakout Buy Order")

  elif current_price < support:
    entry_price = tick.bid
    sl = entry_price + (300 * point)
    tp = entry_price - (600 * point)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_SELL,
        "price": entry_price,
        "sl": float(sl),
        "tp": float(tp),
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "GoldSense Hardened Sell",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    handle_order_result(result, "Breakout Sell Order")


def manage_positions():
  if not ensure_connection():
    return
  symbol_info = mt5.symbol_info(SYMBOL)
  if symbol_info is None:
    return
  point = symbol_info.point
  tick = mt5.symbol_info_tick(SYMBOL)
  if not tick:
    return

  positions = mt5.positions_get(symbol=SYMBOL)
  if not positions:
    return

  trail_distance = 250 * point
  be_trigger = 400 * point
  safety_buffer = 15 * point

  for pos in positions:
    if pos.magic != MAGIC_NUMBER:
      continue

    if pos.type == mt5.ORDER_TYPE_BUY:
      profit_points = (tick.bid - pos.price_open) / point
      if profit_points >= be_trigger:
        target_sl = pos.price_open + safety_buffer
        if pos.sl < target_sl:
          req = {
              "action": mt5.TRADE_ACTION_SLTP,
              "symbol": SYMBOL,
              "position": pos.ticket,
              "sl": float(target_sl),
              "tp": float(pos.tp),
          }
          res = mt5.order_send(req)
          handle_order_result(res, f"Move BUY #{pos.ticket} to BE")

      new_sl = tick.bid - trail_distance
      if new_sl > pos.sl and (pos.sl == 0 or new_sl > pos.sl):
        req = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": SYMBOL,
            "position": pos.ticket,
            "sl": float(new_sl),
            "tp": float(pos.tp),
        }
        res = mt5.order_send(req)
        handle_order_result(res, f"Trail BUY #{pos.ticket}")

    elif pos.type == mt5.ORDER_TYPE_SELL:
      profit_points = (pos.price_open - tick.ask) / point
      if profit_points >= be_trigger:
        target_sl = pos.price_open - safety_buffer
        if pos.sl == 0 or pos.sl > target_sl:
          req = {
              "action": mt5.TRADE_ACTION_SLTP,
              "symbol": SYMBOL,
              "position": pos.ticket,
              "sl": float(target_sl),
              "tp": float(pos.tp),
          }
          res = mt5.order_send(req)
          handle_order_result(res, f"Move SELL #{pos.ticket} to BE")

      new_sl = tick.ask + trail_distance
      if pos.sl == 0 or new_sl < pos.sl:
        req = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": SYMBOL,
            "position": pos.ticket,
            "sl": float(new_sl),
            "tp": float(pos.tp),
        }
        res = mt5.order_send(req)
        handle_order_result(res, f"Trail SELL #{pos.ticket}")


if __name__ == "__main__":
  if initialize_mt5():
    print("GoldSense Hardened Trading Engine initialized successfully.")
    try:
      while True:
        sync_telemetry()
        check_breakout_entry()
        manage_positions()
        time.sleep(10)
    except KeyboardInterrupt:
      mt5.shutdown()
      print("Engine stopped safely by user.")