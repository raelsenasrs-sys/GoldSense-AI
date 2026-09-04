import json
import os
import pandas as pd

class SelfLearnerEngine:
    """
    Manages historical trade logging, feature recording, 
    and dynamic parameter adaptation for GoldSense AI.
    """
    def __init__(self, storage_file="goldsense_memory.json"):
        self.storage_file = storage_file
        self.memory = self.load_memory()

    def load_memory(self) -> list:
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_memory(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def log_completed_trade(self, market_features: dict, trade_result: dict):
        """Appends the market state and trade outcome for future adaptation."""
        record = {
            "features": market_features,
            "result": trade_result  # Contains pnl, return_r, success (bool)
        }
        self.memory.append(record)
        self.save_memory()
        self.optimize_parameters()

    def optimize_parameters(self):
        """Analyzes accumulated data to adapt rules (e.g., disable underperforming sessions)."""
        if len(self.memory) < 10:
            return  # Wait for a meaningful sample size
            
        df = pd.DataFrame([
            {**item['features'], **item['result']} for item in self.memory
        ])

        # Example self-learning rule: If win rate in a specific session drops below 35%, flag it
        if 'session' in df.columns and 'success' in df.columns:
            session_stats = df.groupby('session')['success'].mean()
            for session, win_rate in session_stats.items():
                if win_rate < 0.35:
                    print(f"[Self-Learner AI] Warning: Session '{session}' win rate is low ({win_rate:.2f}). Tightening entry filter for this period.")