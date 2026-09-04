class RiskManagerBrain2:
    """
    Brain 2: Risk Manager for GoldSense AI (XAUUSD Scalper).
    Enforces absolute veto rules, position sizing, and capital protection.
    """
    def __init__(self, account_balance=10000.0, risk_per_trade_pct=1.0, 
                 max_daily_loss_pct=3.0, max_consecutive_losses=3):
        self.account_balance = account_balance
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_daily_loss = account_balance * (max_daily_loss_pct / 100.0)
        self.max_consecutive_losses = max_consecutive_losses
        
        # State trackers
        self.current_daily_pnl = 0.0
        self.current_consecutive_losses = 0

    def check_veto_conditions(self, brain1_output: dict, trade_setup: dict, macro_status: dict) -> tuple:
        """Evaluates all veto triggers. Returns (is_vetoed: bool, reasons: list)."""
        veto_reasons = []

        # 1. Daily Loss Limit Check
        if self.current_daily_pnl <= -self.max_daily_loss:
            veto_reasons.append("DAILY_LOSS_LIMIT_REACHED")

        # 2. Consecutive Loss Limit Check
        if self.current_consecutive_losses >= self.max_consecutive_losses:
            veto_reasons.append("CONSECUTIVE_LOSS_LIMIT_REACHED")

        # 3. Volatility & Spread Check (from Brain 1)
        if not brain1_output.get("volatility_metrics", {}).get("volatility_acceptable", True):
            veto_reasons.append("SPREAD_TOO_HIGH_OR_LOW_VOLATILITY")

        # 4. Major News Approaching (from Macro status)
        if macro_status.get("high_impact_news_approaching", False):
            veto_reasons.append("MAJOR_NEWS_APPROACHING")

        # 5. Reward-to-Risk Check
        min_rr = 1.5
        if trade_setup.get("reward_to_risk", 0.0) < min_rr:
            veto_reasons.append("POOR_REWARD_TO_RISK")

        # 6. Trend Alignment Check
        trend_align = brain1_output.get("trend_alignment", {})
        if not trend_align.get("alignment", False) and trade_setup.get("is_counter_trend", False):
            veto_reasons.append("COUNTER_TREND_SETUP_REJECTED")

        is_vetoed = len(veto_reasons) > 0
        return is_vetoed, veto_reasons

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculates precise lot size for XAUUSD based on risk percentage."""
        risk_amount = self.account_balance * (self.risk_per_trade_pct / 100.0)
        price_risk_pips = abs(entry_price - stop_loss)
        
        if price_risk_pips == 0:
            return 0.0

        # Standard XAUUSD contract size calculation (1 standard lot = 100 oz)
        contract_size = 100.0
        lot_size = risk_amount / (price_risk_pips * contract_size)
        return round(lot_size, 2)

    def evaluate_risk(self, brain1_output: dict, trade_setup: dict, macro_status: dict) -> dict:
        """Executes Brain 2 comprehensive evaluation and returns final risk verdict."""
        is_vetoed, reasons = self.check_veto_conditions(brain1_output, trade_setup, macro_status)

        if is_vetoed:
            return {
                "verdict": "VETO",
                "action": "NO TRADE",
                "reasons": reasons,
                "position_size": 0.0
            }

        # Calculate safe size if approved
        lot_size = self.calculate_position_size(trade_setup["entry"], trade_setup["stop_loss"])

        return {
            "verdict": "APPROVE",
            "action": "EXECUTE",
            "reasons": [],
            "position_size": lot_size
        }