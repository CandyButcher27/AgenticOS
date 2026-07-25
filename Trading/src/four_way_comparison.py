from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import data
import strategy
import backtest
import metrics
from sweep_stop_loss import START, END, run_sweep, GRID
from sweep_stop_loss_by_year import best_practical_factor

OUT_DIR = Path(__file__).parent.parent / "runs" / "four_way_comparison"
K_B = 0.85
TEST_YEARS = range(2022, 2026)  # D needs >=2 prior years, unavailable for 2020/2021

COLORS = {"A_no_stop": "#9ca3af", "B_fixed": "#2563eb", "C_prior_year": "#dc2626", "D_expanding": "#16a34a"}
LABELS = {
    "A_no_stop": "A: no stop",
    "B_fixed": "B: fixed k=0.85",
    "C_prior_year": "C: prior-year k",
    "D_expanding": "D: expanding-window k",
}


def trade_year(weeks_year, spy, vix, irx, k=None):
    weeks = strategy.disable_stop(weeks_year) if k is None else strategy.add_stop_bounds(weeks_year, stop_loss_factor=k)
    return backtest.run(weeks, spy, vix, irx)


def best_factor_for_window(weeks_base, spy, vix, irx, years):
    window_weeks = weeks_base[weeks_base["entry_date"].dt.year.isin(years)]
    results = run_sweep(window_weeks, spy, vix, irx)
    row = best_practical_factor(results)
    return row["stop_loss_factor"] if row is not None else K_B


def main():
    raw = data.get_all(START, END)
    weeks_base = strategy.generate_weeks(raw["spy"], raw["vix"], raw["irx"])
    weeks_base["entry_date"] = pd.to_datetime(weeks_base["entry_date"])
    spy, vix, irx = raw["spy"], raw["vix"], raw["irx"]

    rows = []
    trades_by_approach = {"A_no_stop": [], "B_fixed": [], "C_prior_year": [], "D_expanding": []}

    for year in TEST_YEARS:
        weeks_year = weeks_base[weeks_base["entry_date"].dt.year == year]

        k_c = best_factor_for_window(weeks_base, spy, vix, irx, [year - 1])
        k_d = best_factor_for_window(weeks_base, spy, vix, irx, range(2020, year))

        trades_a = trade_year(weeks_year, spy, vix, irx, k=None)
        trades_b = trade_year(weeks_year, spy, vix, irx, k=K_B)
        trades_c = trade_year(weeks_year, spy, vix, irx, k=k_c)
        trades_d = trade_year(weeks_year, spy, vix, irx, k=k_d)

        for key, trades in [("A_no_stop", trades_a), ("B_fixed", trades_b), ("C_prior_year", trades_c), ("D_expanding", trades_d)]:
            trades_by_approach[key].append(trades)

        m_a, m_b, m_c, m_d = (metrics.compute(t) for t in [trades_a, trades_b, trades_c, trades_d])
        rows.append(
            {
                "year": year,
                "pnl_A": m_a["total_pnl"], "sharpe_A": m_a["sharpe_ratio"],
                "pnl_B": m_b["total_pnl"], "sharpe_B": m_b["sharpe_ratio"],
                "k_C": k_c, "pnl_C": m_c["total_pnl"], "sharpe_C": m_c["sharpe_ratio"],
                "k_D": k_d, "pnl_D": m_d["total_pnl"], "sharpe_D": m_d["sharpe_ratio"],
            }
        )

    yearly = pd.DataFrame(rows).set_index("year")

    combined_rows = []
    for key in trades_by_approach:
        m = metrics.compute(pd.concat(trades_by_approach[key], ignore_index=True))
        combined_rows.append({"approach": LABELS[key], **m})
    combined = pd.DataFrame(combined_rows)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    yearly.to_csv(OUT_DIR / "four_way_by_year.csv")
    combined.to_csv(OUT_DIR / "four_way_combined.csv", index=False)
    plot(yearly, OUT_DIR / "four_way_plot.png")

    print(yearly.to_string())
    print()
    print(combined[["approach", "total_pnl", "sharpe_ratio", "max_drawdown", "win_rate"]].to_string(index=False))


def plot(yearly, out_path):
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    fig.suptitle("A: no stop  vs  B: fixed k=0.85  vs  C: prior-year k  vs  D: expanding-window k")

    x = range(len(yearly))
    width = 0.2
    keys = ["A", "B", "C", "D"]
    colors = [COLORS["A_no_stop"], COLORS["B_fixed"], COLORS["C_prior_year"], COLORS["D_expanding"]]
    labels = [LABELS["A_no_stop"], LABELS["B_fixed"], LABELS["C_prior_year"], LABELS["D_expanding"]]

    for i, (k, color, label) in enumerate(zip(keys, colors, labels)):
        offset = (i - 1.5) * width
        axes[0].bar([xi + offset for xi in x], yearly[f"pnl_{k}"], width, color=color, label=label)
        axes[1].bar([xi + offset for xi in x], yearly[f"sharpe_{k}"], width, color=color, label=label)

    axes[0].set_title("Total P&L by year", loc="left", fontsize=10)
    axes[0].yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    axes[0].legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    axes[1].set_title("Sharpe ratio by year", loc="left", fontsize=10)

    for ax in axes:
        ax.set_xticks(list(x))
        ax.set_xticklabels(yearly.index)
        ax.grid(color=GRID, linewidth=0.8, axis="y")
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    main()
