import pandas as pd

import blackscholes
import backtest
from strategy import round_strikes, round_stop_bounds


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


def test_stop_bound_rounding():
    # L rounds up (toward spot), U rounds down (toward spot)
    L_stop, U_stop = round_stop_bounds(L_stop_raw=397.3, U_stop_raw=402.7, strike_increment=1)
    assert L_stop == 398
    assert U_stop == 402


ENTRY = pd.Timestamp("2024-01-01")
EXPIRY = pd.Timestamp("2024-01-05")


def _daily_frame(rows):
    # rows: dict of {date: (spot, vix, irx)}
    index = list(rows.keys())
    return (
        pd.DataFrame({"close": [rows[d][0] for d in index]}, index=index),
        pd.DataFrame({"close": [rows[d][1] for d in index]}, index=index),
        pd.DataFrame({"close": [rows[d][2] for d in index]}, index=index),
    )


def _make_week(spot_expiry, strike_put=395, strike_call=405, L_stop=380, U_stop=420):
    weeks = pd.DataFrame(
        [
            {
                "entry_date": ENTRY,
                "expiry_date": EXPIRY,
                "spot_entry": 400,
                "spot_expiry": spot_expiry,
                "strike_put": strike_put,
                "strike_call": strike_call,
                "premium_put": 1.0,
                "premium_call": 1.0,
                "L_stop": L_stop,
                "U_stop": U_stop,
            }
        ]
    )
    spy, vix, irx = _daily_frame(
        {ENTRY: (400, 20, 5), EXPIRY: (spot_expiry, 20, 5)}
    )
    return weeks, spy, vix, irx


def test_payoff_both_legs_otm():
    weeks, spy, vix, irx = _make_week(spot_expiry=400)
    trades = backtest.run(weeks, spy, vix, irx)
    assert trades.loc[0, "exit_reason"] == "expiry"
    assert trades.loc[0, "payout"] == 0
    assert trades.loc[0, "pnl"] == 200  # premium_total kept, no payout


def test_payoff_put_itm():
    weeks, spy, vix, irx = _make_week(spot_expiry=390)
    trades = backtest.run(weeks, spy, vix, irx)
    assert trades.loc[0, "payout"] == 500  # (395-390)*100
    assert trades.loc[0, "pnl"] == 200 - 500


def test_payoff_call_itm():
    weeks, spy, vix, irx = _make_week(spot_expiry=410)
    trades = backtest.run(weeks, spy, vix, irx)
    assert trades.loc[0, "payout"] == 500  # (410-405)*100
    assert trades.loc[0, "pnl"] == 200 - 500


def test_stop_loss_triggers_and_reprices():
    mid_date = pd.Timestamp("2024-01-03")
    weeks = pd.DataFrame(
        [
            {
                "entry_date": ENTRY,
                "expiry_date": EXPIRY,
                "spot_entry": 400,
                "spot_expiry": 350,  # far ITM at expiry, but should never get here
                "strike_put": 395,
                "strike_call": 405,
                "premium_put": 1.0,
                "premium_call": 1.0,
                "L_stop": 398,  # tight bound, breached mid-week
                "U_stop": 402,
            }
        ]
    )
    spy, vix, irx = _daily_frame(
        {
            ENTRY: (400, 20, 5),
            mid_date: (390, 22, 5),  # breaches L_stop=398
            EXPIRY: (350, 25, 5),
        }
    )
    trades = backtest.run(weeks, spy, vix, irx)
    row = trades.loc[0]
    assert row["exit_reason"] == "stop_loss"
    assert row["exit_date"] == mid_date
    assert row["spot_exit"] == 390

    T_remaining = (EXPIRY - mid_date).days / 365
    expected_buyback = (
        blackscholes.put_price(390, 395, T_remaining, 0.05, 0.22)
        + blackscholes.call_price(390, 405, T_remaining, 0.05, 0.22)
    ) * 100
    assert abs(row["payout"] - expected_buyback) < 1e-9
    assert abs(row["pnl"] - (200 - expected_buyback)) < 1e-9


def test_stop_loss_not_triggered_stays_to_expiry():
    mid_date = pd.Timestamp("2024-01-03")
    weeks = _make_week(spot_expiry=400, L_stop=380, U_stop=420)[0]
    spy, vix, irx = _daily_frame(
        {
            ENTRY: (400, 20, 5),
            mid_date: (405, 20, 5),  # within [380, 420], no breach
            EXPIRY: (400, 20, 5),
        }
    )
    trades = backtest.run(weeks, spy, vix, irx)
    assert trades.loc[0, "exit_reason"] == "expiry"
