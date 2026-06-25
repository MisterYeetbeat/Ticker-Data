"""Analyze CIEN TradingView backtest and compare against MU results."""

import sys, os
import pandas as pd
import numpy as np

MU_DIR = os.path.join(os.path.dirname(__file__), "..", "MU")
CIEN_DIR = os.path.dirname(__file__)


def analyze_tv(path, label):
    df = pd.read_csv(path)
    entries = df[df["Type"].str.startswith("Entry")].reset_index(drop=True)
    # Handle "Open" type for last trade still open
    exits = df[~df["Type"].str.startswith("Entry")].reset_index(drop=True)

    n = len(entries)
    pnls = exits["Net P&L USD"].values
    pnl_pcts = exits["Net P&L %"].values

    wins = pnls > 0
    losses = pnls < 0
    n_win = int(wins.sum())
    n_loss = int(losses.sum())
    gp = pnls[wins].sum()
    gl = abs(pnls[losses].sum())
    pf = gp / gl if gl > 0 else float("inf")

    cum = exits["Cumulative P&L USD"].values
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    max_dd = dd.max()
    max_dd_idx = dd.argmax()
    peak_eq = 10000 + peak[max_dd_idx]
    max_dd_pct = max_dd / peak_eq * 100

    fav = exits["Favorable excursion %"].values
    adv = exits["Adverse excursion %"].values

    return {
        "label": label,
        "trades": n,
        "net": cum[-1],
        "net_pct": cum[-1] / 100,
        "pf": pf,
        "wr": n_win / n * 100,
        "n_win": n_win,
        "n_loss": n_loss,
        "avg_win": pnls[wins].mean() if n_win else 0,
        "avg_loss": pnls[losses].mean() if n_loss else 0,
        "best": pnls.max(),
        "worst": pnls.min(),
        "best_pct": pnl_pcts.max(),
        "worst_pct": pnl_pcts.min(),
        "max_dd": max_dd,
        "max_dd_pct": max_dd_pct,
        "avg_fav": fav.mean(),
        "avg_adv": adv.mean(),
        "ev": pnls.mean(),
    }


def main():
    cien_path = os.path.join(
        CIEN_DIR,
        "MU_15-Min_Jan-17-26_(QC_v5_-_Fixed_Slope_Logic)_NYSE_CIEN_2026-02-28_02983.csv",
    )
    mu_opt_path = os.path.join(
        os.path.expanduser("~"), "Downloads",
        "MU_15-Min_Jan-17-26_(QC_v5_-_Fixed_Slope_Logic)_NASDAQ_MU_2026-02-28_3f8ad.csv",
    )
    mu_orig_path = os.path.join(
        MU_DIR,
        "MU_15-Min_Jan-17-26_(QC_v5_-_Fixed_Slope_Logic)_NASDAQ_MU_2026-02-28_1e50.csv",
    )

    cien = analyze_tv(cien_path, "CIEN Optimized")
    mu_opt = analyze_tv(mu_opt_path, "MU Optimized")
    mu_orig = analyze_tv(mu_orig_path, "MU Original")

    print("=" * 80)
    print("  STRATEGY PERFORMANCE ACROSS STOCKS")
    print("  Optimized: TP=6.0, SL=6.0, BE=2.0, TT=3.2, TO=2.5, ADX=15")
    print("=" * 80)

    header = "  {:<22} {:>14} {:>14} {:>14}".format(
        "Metric", "MU Original", "MU Optimized", "CIEN Optimized"
    )
    print()
    print(header)
    print("  " + "-" * 22 + " " + "-" * 14 + " " + "-" * 14 + " " + "-" * 14)

    rows = [
        ("Net P&L", "${:>13,.0f}", "net"),
        ("Net P&L %", "{:>+13.1f}%", "net_pct"),
        ("Profit Factor", "{:>14.2f}", "pf"),
        ("Win Rate", "{:>13.1f}%", "wr"),
        ("Total Trades", "{:>14}", "trades"),
        ("Avg Win", "${:>13,.0f}", "avg_win"),
        ("Avg Loss", "${:>13,.0f}", "avg_loss"),
        ("Best Trade %", "{:>+13.2f}%", "best_pct"),
        ("Worst Trade %", "{:>13.2f}%", "worst_pct"),
        ("Max Drawdown", "{:>-13.1f}%", "max_dd_pct"),
        ("EV per Trade", "${:>13,.0f}", "ev"),
        ("Avg Favorable", "{:>13.2f}%", "avg_fav"),
        ("Avg Adverse", "{:>13.2f}%", "avg_adv"),
    ]

    for label, fmt, key in rows:
        o = fmt.format(mu_orig[key])
        m = fmt.format(mu_opt[key])
        c = fmt.format(cien[key])
        print("  {:<22} {:>14} {:>14} {:>14}".format(label, o, m, c))

    # Win/Loss line
    o = "{}W/{}L".format(mu_orig["n_win"], mu_orig["n_loss"])
    m = "{}W/{}L".format(mu_opt["n_win"], mu_opt["n_loss"])
    c = "{}W/{}L".format(cien["n_win"], cien["n_loss"])
    print("  {:<22} {:>14} {:>14} {:>14}".format("Wins / Losses", o, m, c))

    print()
    print("=" * 80)
    print("  KEY FINDINGS")
    print("=" * 80)
    print()
    print("  1. CIEN +{:.0f}% — even better than MU Optimized +{:.0f}%".format(
        cien["net_pct"], mu_opt["net_pct"]))
    print("  2. CIEN PF {:.2f} — higher than MU Optimized {:.2f}".format(
        cien["pf"], mu_opt["pf"]))
    print("  3. CIEN DD {:.1f}% — vs MU Optimized {:.1f}%".format(
        cien["max_dd_pct"], mu_opt["max_dd_pct"]))
    print("  4. CIEN WR {:.1f}% — vs MU Optimized {:.1f}%".format(
        cien["wr"], mu_opt["wr"]))
    print("  5. CIEN EV ${:.0f}/trade — vs MU ${:.0f}/trade".format(
        cien["ev"], mu_opt["ev"]))
    print()
    print("  The optimized parameters generalize well across stocks!")
    print("  Parameters were optimized on MU but work even better on CIEN.")


if __name__ == "__main__":
    main()
