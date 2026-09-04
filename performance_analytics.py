import pandas as pd
import numpy as np

class PerformanceAnalytics:
    """
    Performance Analytics Module for GoldSense AI.
    Tracks win rates, profit factor, expectancy, drawdown, and session profiles.
    """
    def __init__(self):
        self.trade_history = []

    def record_trade(self, trade_data: dict):
        """Records a completed trade into the analytics ledger."""
        self.trade_history.append({
            "pnl": trade_data.get("pnl", 0.0),
            "return_r": trade_data.get("return_r", 0.0),
            "session": trade_data.get("session", "UNKNOWN"),
            "setup_type": trade_data.get("setup_type", "BREAKOUT"),
            "holding_time_mins": trade_data.get("holding_time_mins", 0),
            "is_win": trade_data.get("pnl", 0.0) > 0
        })

    def calculate_metrics(self) -> dict:
        """Computes core quantitative performance metrics."""
        if not self.trade_history:
            return {"status": "No trades recorded yet."}

        df = pd.DataFrame(self.trade_history)
        total_trades = len(df)
        winning_trades = df[df['is_win']]
        losing_trades = df[~df['is_win']]

        # Win Rate
        win_rate = (len(winning_trades) / total_trades) * 100.0

        # Profit Factor (Gross Profits / Gross Losses)
        gross_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0.0
        gross_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf

        # Expectancy
        win_pct = len(winning_trades) / total_trades
        loss_pct = len(losing_trades) / total_trades
        avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0.0
        avg_loss = abs(losing_trades['pnl'].mean()) if not losing_trades.empty else 0.0
        expectancy = (win_pct * avg_win) - (loss_pct * avg_loss)

        # Max Drawdown from cumulative PnL equity curve
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['peak'] = df['cumulative_pnl'].cummax()
        df['drawdown'] = df['peak'] - df['cumulative_pnl']
        max_drawdown = df['drawdown'].max() if not df.empty else 0.0

        # Averages
        avg_holding_time = df['holding_time_mins'].mean()
        avg_r_multiple = df['return_r'].mean()

        # Best / Worst Session analysis
        session_performance = df.groupby('session')['pnl'].sum()
        best_session = session_performance.idxmax() if not session_performance.empty else "N/A"
        worst_session = session_performance.idxmin() if not session_performance.empty else "N/A"

        return {
            "total_trades": total_trades,
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy_dollars": round(expectancy, 2),
            "max_drawdown": round(max_drawdown, 2),
            "avg_r_multiple": round(avg_r_multiple, 2),
            "avg_holding_time_mins": round(avg_holding_time, 1),
            "best_trading_session": best_session,
            "worst_trading_session": worst_session
        }