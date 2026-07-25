from pathlib import Path

import data
import strategy
import backtest
import metrics

START = "2020-01-01"
END = "2025-12-31"
RESULTS_DIR = Path(__file__).parent.parent / "results"


def main():
    raw = data.get_all(START, END)
    weeks = strategy.generate_weeks(raw["spy"], raw["vix"], raw["irx"])
    trades = backtest.run(weeks)

    RESULTS_DIR.mkdir(exist_ok=True)
    trades.to_csv(RESULTS_DIR / "trades.csv", index=False)

    summary = metrics.compute(trades)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
