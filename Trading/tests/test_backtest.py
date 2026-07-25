import pandas as pd

import blackscholes
import backtest
from strategy import round_strikes


def test_black_scholes_known_value():
    # Hull's textbook example: S=42, K=40, T=0.5, r=0.1, sigma=0.2 -> call ~4.76
    price = blackscholes.call_price(42, 40, 0.5, 0.1, 0.2)
    assert abs(price - 4.76) < 0.01


def test_strike_rounding_default_increment():
    strike_put, strike_call = round_strikes(L=397.3, U=402.7, strike_increment=1)
    assert strike_put == 397
    assert strike_call == 403


def test_strike_rounding_custom_increment():
    strike_put, strike_call = round_strikes(L=397.3, U=402.7, strike_increment=5)
    assert strike_put == 395
    assert strike_call == 405


def _make_week(spot_expiry, strike_put=395, strike_call=405):
    return pd.DataFrame(
        [
            {
                "entry_date": pd.Timestamp("2024-01-01"),
                "expiry_date": pd.Timestamp("2024-01-05"),
                "spot_entry": 400,
                "spot_expiry": spot_expiry,
                "strike_put": strike_put,
                "strike_call": strike_call,
                "premium_put": 1.0,
                "premium_call": 1.0,
            }
        ]
    )


def test_payoff_both_legs_otm():
    trades = backtest.run(_make_week(spot_expiry=400))
    assert trades.loc[0, "payout"] == 0
    assert trades.loc[0, "pnl"] == 200  # premium_total kept, no payout


def test_payoff_put_itm():
    trades = backtest.run(_make_week(spot_expiry=390))
    assert trades.loc[0, "payout"] == 500  # (395-390)*100
    assert trades.loc[0, "pnl"] == 200 - 500


def test_payoff_call_itm():
    trades = backtest.run(_make_week(spot_expiry=410))
    assert trades.loc[0, "payout"] == 500  # (410-405)*100
    assert trades.loc[0, "pnl"] == 200 - 500
