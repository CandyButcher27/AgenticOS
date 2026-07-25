import math

import pandas as pd

import blackscholes


def round_strikes(L, U, strike_increment=1):
    strike_put = math.floor(L / strike_increment) * strike_increment
    strike_call = math.ceil(U / strike_increment) * strike_increment
    return strike_put, strike_call


def round_stop_bounds(L_stop_raw, U_stop_raw, strike_increment=1):
    L_stop = math.ceil(L_stop_raw / strike_increment) * strike_increment
    U_stop = math.floor(U_stop_raw / strike_increment) * strike_increment
    return L_stop, U_stop


def merge_daily(spy, vix, irx):
    return pd.DataFrame(
        {"spot": spy["close"], "vix": vix["close"], "irx": irx["close"]}
    ).dropna()


def generate_weeks(spy, vix, irx, strike_increment=1):
    merged = merge_daily(spy, vix, irx)
    merged["iso_year"] = merged.index.isocalendar().year
    merged["iso_week"] = merged.index.isocalendar().week

    rows = []
    for (_, _), group in merged.groupby(["iso_year", "iso_week"]):
        group = group.sort_index()
        entry_date = group.index[0]
        expiry_date = group.index[-1]
        if entry_date == expiry_date:
            continue  # only one trading day this week, can't form a weekly trade

        spot_entry = group.loc[entry_date, "spot"]
        spot_expiry = group.loc[expiry_date, "spot"]
        iv_proxy = group.loc[entry_date, "vix"] / 100
        rate = group.loc[entry_date, "irx"] / 100
        days_to_expiry = (expiry_date - entry_date).days
        T = days_to_expiry / 365

        expected_move = spot_entry * iv_proxy * math.sqrt(T)
        L = spot_entry - expected_move
        U = spot_entry + expected_move
        strike_put, strike_call = round_strikes(L, U, strike_increment)

        premium_put = blackscholes.put_price(spot_entry, strike_put, T, rate, iv_proxy)
        premium_call = blackscholes.call_price(spot_entry, strike_call, T, rate, iv_proxy)

        rows.append(
            {
                "entry_date": entry_date,
                "expiry_date": expiry_date,
                "spot_entry": spot_entry,
                "spot_expiry": spot_expiry,
                "iv_proxy": iv_proxy,
                "rate": rate,
                "days_to_expiry": days_to_expiry,
                "expected_move": expected_move,
                "L": L,
                "U": U,
                "strike_put": strike_put,
                "strike_call": strike_call,
                "premium_put": premium_put,
                "premium_call": premium_call,
            }
        )

    return pd.DataFrame(rows)


def add_stop_bounds(weeks_df, stop_loss_factor=0.95, strike_increment=1):
    df = weeks_df.copy()
    stop_move = df["expected_move"] * stop_loss_factor
    L_stop_raw = df["spot_entry"] - stop_move
    U_stop_raw = df["spot_entry"] + stop_move
    df["L_stop"] = (L_stop_raw / strike_increment).apply(math.ceil) * strike_increment
    df["U_stop"] = (U_stop_raw / strike_increment).apply(math.floor) * strike_increment
    return df
