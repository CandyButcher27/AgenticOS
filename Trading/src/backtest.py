import pandas as pd

import blackscholes
import strategy


def _settle_at_expiry(trade):
    payout = (
        max(0, trade["strike_put"] - trade["spot_expiry"]) * 100
        + max(0, trade["spot_expiry"] - trade["strike_call"]) * 100
    )
    return trade["expiry_date"], "expiry", trade["spot_expiry"], payout


def _check_stop_loss(trade, mid_days):
    for exit_date, day in mid_days.iterrows():
        spot_day = day["spot"]
        if spot_day <= trade["L_stop"] or spot_day >= trade["U_stop"]:
            T_remaining = (trade["expiry_date"] - exit_date).days / 365
            iv_exit = day["vix"] / 100
            rate_exit = day["irx"] / 100
            buyback_put = blackscholes.put_price(
                spot_day, trade["strike_put"], T_remaining, rate_exit, iv_exit
            )
            buyback_call = blackscholes.call_price(
                spot_day, trade["strike_call"], T_remaining, rate_exit, iv_exit
            )
            payout = (buyback_put + buyback_call) * 100
            return exit_date, "stop_loss", spot_day, payout
    return None


def run(weeks_df, spy, vix, irx):
    daily = strategy.merge_daily(spy, vix, irx)

    records = []
    for _, trade in weeks_df.iterrows():
        mid_days = daily.loc[trade["entry_date"] : trade["expiry_date"]].iloc[1:-1]
        result = _check_stop_loss(trade, mid_days)
        if result is None:
            result = _settle_at_expiry(trade)
        exit_date, exit_reason, spot_exit, payout = result

        premium_total = (trade["premium_put"] + trade["premium_call"]) * 100
        pnl = premium_total - payout
        capital_proxy = trade["strike_put"] * 100

        record = trade.to_dict()
        record.update(
            {
                "premium_total": premium_total,
                "exit_date": exit_date,
                "exit_reason": exit_reason,
                "spot_exit": spot_exit,
                "payout": payout,
                "pnl": pnl,
                "capital_proxy": capital_proxy,
                "return_pct": pnl / capital_proxy,
            }
        )
        records.append(record)

    return pd.DataFrame(records)
