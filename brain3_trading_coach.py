import datetime

class TradingCoachBrain3:
    """
    Brain 3: Trading Coach for GoldSense AI (XAUUSD Scalper).
    Evaluates trader discipline, tracks psychological patterns, and provides post-trade coaching.
    """
    def __init__(self):
        self.behavioral_log = []
        self.trade_journal = []

    def evaluate_discipline(self, trade_intent: dict) -> dict:
        """Evaluates if the proposed trade aligns with rules and flags behavioral risks."""
        warnings = []
        
        # Check for potential behavioral red flags
        if trade_intent.get("rapid_successive_trade", False):
            warnings.append("POTENTIAL_REVENGE_OR_OVERTRADING")
        
        if trade_intent.get("chasing_price", False):
            warnings.append("FOMO_ENTRY_DETECTED")

        score = 100 - (len(warnings) * 25)
        return {
            "discipline_score": max(score, 0),
            "behavioral_warnings": warnings,
            "coach_commentary": "Maintain composure. Wait for high-probability setups." if warnings else "Discipline standards met."
        }

    def log_trade_outcome(self, trade_record: dict, trader_emotions: str) -> None:
        """Records trade data along with emotional state and AI critique."""
        record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "trade_data": trade_record,
            "emotions": trader_emotions,
            "violated_rules": trade_record.get("violations", [])
        }
        self.trade_journal.append(record)

    def generate_coaching_review(self) -> dict:
        """Summarizes performance patterns, psychological leaks, and areas for improvement."""
        if not self.trade_journal:
            return {"status": "No trade data available for review."}

        total_trades = len(self.trade_journal)
        violation_counts = sum(len(t["violated_rules"]) for t in self.trade_journal)

        return {
            "total_logged_trades": total_trades,
            "total_rule_violations": violation_counts,
            "coaching_summary": "Focus on eliminating FOMO entries and strictly respecting daily loss thresholds."
        }