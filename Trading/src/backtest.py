def run(weeks_df):
    df = weeks_df.copy()
    df["premium_total"] = (df["premium_put"] + df["premium_call"]) * 100
    df["payout"] = (
        (df["strike_put"] - df["spot_expiry"]).clip(lower=0) * 100
        + (df["spot_expiry"] - df["strike_call"]).clip(lower=0) * 100
    )
    df["pnl"] = df["premium_total"] - df["payout"]
    df["capital_proxy"] = df["strike_put"] * 100
    df["return_pct"] = df["pnl"] / df["capital_proxy"]
    return df
