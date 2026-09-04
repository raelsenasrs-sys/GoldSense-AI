from mt5_bridge import MT5Bridge
from brain1_market_analyst import MarketAnalystBrain1
from brain2_risk_manager import RiskManagerBrain2
from brain3_trading_coach import TradingCoachBrain3
from self_learner import SelfLearnerEngine

def run_autonomous_pipeline():
    print("Launching GoldSense AI Autonomous Execution & Learning Engine...")

    bridge = MT5Bridge(symbol="XAUUSD")
    if not bridge.connect():
        return

    learner = SelfLearnerEngine()
    df_history = bridge.fetch_live_rates(num_bars=150)
    if df_history.empty:
        bridge.disconnect()
        return

    df_ltf = df_history.tail(50).copy()
    df_htf = df_history.copy()

    brain1 = MarketAnalystBrain1(symbol="XAUUSD")
    brain2 = RiskManagerBrain2(account_balance=10000.0, risk_per_trade_pct=1.0)
    brain3 = TradingCoachBrain3()

    # 1. Analyze Market State
    market_intelligence = brain1.run_analysis(df_ltf, df_htf)
    latest_close = float(df_ltf['close'].iloc[-1])
    atr_val = market_intelligence['volatility_metrics']['atr']

    trade_setup = {
        "entry": latest_close,
        "stop_loss": round(latest_close - (atr_val * 0.6), 2),
        "take_profit": round(latest_close + (atr_val * 1.5), 2),
        "reward_to_risk": 2.5,
        "is_counter_trend": False
    }

    macro_status = {"high_impact_news_approaching": False}

    # 2. Risk Evaluation & Veto Check
    risk_evaluation = brain2.evaluate_risk(market_intelligence, trade_setup, macro_status)
    discipline_report = brain3.evaluate_discipline({"rapid_successive_trade": False, "chasing_price": False})

    # 3. Autonomous Execution Workflow
    if risk_evaluation['action'] == "EXECUTE" and discipline_report['discipline_score'] >= 75:
        print(f"\n[Autonomous Execution] Conditions met. Executing order on MT5...")
        
        # Uncomment to execute live order via MT5 bridge:
        # success = bridge.execute_order("BUY", risk_evaluation['position_size'], latest_close, trade_setup['stop_loss'], trade_setup['take_profit'])
        
        # Mocking simulated execution return for demonstration loop:
        simulated_trade_success = True 
        simulated_pnl = 145.50
        simulated_r = 2.1

        # 4. Feed Data Back to Self-Learner Engine
        market_features_snapshot = {
            "market_phase": market_intelligence['market_phase'],
            "volatility": atr_val,
            "session": "LONDON" # Example session tag
        }
        
        trade_result_snapshot = {
            "pnl": simulated_pnl,
            "return_r": simulated_r,
            "success": simulated_trade_success
        }

        learner.log_completed_trade(market_features_snapshot, trade_result_snapshot)
        print("[Self-Learner] Trade recorded to memory database. Weights optimized.")
    else:
        print("\n[Autonomous Execution] NO TRADE / WAIT. Strict selectivity upheld. Capital safe.")

    bridge.disconnect()

if __name__ == "__main__":
    run_autonomous_pipeline()