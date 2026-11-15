"""Data loading and calculations for the Nigeria Domestic Flight Delay Tracker.

Kept separate from app.py so the logic can be tested without Streamlit.
"""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "ncaa_disruptions.csv"
ALL = "ALL AIRLINES"

BUCKET_COLUMNS = ["delayed_16_60min", "delayed_1_2h", "delayed_2_3h", "delayed_3h_plus"]
BUCKET_LABELS = {
    "delayed_16_60min": "16 min to 1 h",
    "delayed_1_2h": "1 to 2 h",
    "delayed_2_3h": "2 to 3 h",
    "delayed_3h_plus": "3 h and above",
}


def period_label(period: str, period_type: str) -> str:
    """'2026-08','month' -> 'August 2026'; '2026-04','quarter' -> 'Q2 2026'."""
    ts = pd.Timestamp(period + "-01")
    if period_type == "month":
        return ts.strftime("%B %Y")
    return f"Q{(ts.month - 1) // 3 + 1} {ts.year}"


def _rate(numerator: pd.Series, flights: pd.Series) -> pd.Series:
    flights = flights.where(flights > 0)  # 0 flights -> NaN, avoids divide-by-zero
    return numerator / flights


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["label"] = [period_label(p, t) for p, t in zip(df["period"], df["period_type"])]
    df["rate_over_1h"] = _rate(df["delayed_over_1h"], df["total_flights"])
    df["rate_over_15min"] = _rate(df["delayed_over_15min"], df["total_flights"])
    df["cancel_rate"] = _rate(df["cancelled_flights"], df["total_flights"])
    df["notes"] = df["notes"].fillna("")
    return df


def network_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Network-wide monthly rows (all airlines), oldest first."""
    out = df[(df["airline"] == ALL) & (df["period_type"] == "month")]
    return out.sort_values("period").reset_index(drop=True)


def airline_periods(df: pd.DataFrame) -> list:
    """Period labels that have per-airline flight counts, oldest first."""
    rows = df[(df["airline"] != ALL) & (df["total_flights"] > 0)]
    rows = rows.sort_values(["period", "period_type"])
    return list(dict.fromkeys(rows["label"]))


def airline_ranking(df: pd.DataFrame, label: str, rate_column: str, min_flights: int = 0) -> pd.DataFrame:
    """Airlines for one period, highest delay rate first. Drops airlines with too few flights."""
    rows = df[(df["label"] == label) & (df["airline"] != ALL) & (df["total_flights"] >= max(min_flights, 1))]
    rows = rows.dropna(subset=[rate_column])
    return rows.sort_values(rate_column, ascending=False).reset_index(drop=True)


def august_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Delay-length buckets for airlines that report them (August 2026)."""
    rows = df[(df["airline"] != ALL) & df[BUCKET_COLUMNS].notna().any(axis=1) & (df["total_flights"] > 0)]
    return rows.reset_index(drop=True)


def key_findings(df: pd.DataFrame) -> list:
    """Plain-English facts computed from the data, for the Overview tab."""
    findings = []
    monthly = network_monthly(df)
    if monthly.empty:
        return findings
    hi = monthly.loc[monthly["rate_over_1h"].idxmax()]
    lo = monthly.loc[monthly["rate_over_1h"].idxmin()]
    findings.append(
        f"Delays over an hour were highest in {hi['label']} ({hi['rate_over_1h']:.1%} of flights) "
        f"and lowest in {lo['label']} ({lo['rate_over_1h']:.1%})."
    )
    latest = monthly.iloc[-1]
    if pd.notna(latest["rate_over_15min"]):
        findings.append(
            f"In {latest['label']}, {latest['rate_over_15min']:.1%} of flights were delayed by more than 15 minutes "
            f"and {latest['rate_over_1h']:.1%} by more than an hour, according to the NCAA."
        )
        if pd.notna(latest["delayed_3h_plus"]) and latest["delayed_over_15min"] > 0:
            findings.append(
                f"Of the {int(latest['delayed_over_15min']):,} flights delayed in {latest['label']}, "
                f"{int(latest['delayed_3h_plus'])} ({latest['delayed_3h_plus'] / latest['delayed_over_15min']:.1%}) "
                f"were delayed three hours or more."
            )
    ranking = airline_ranking(df, latest["label"], "rate_over_1h", 100)
    if not ranking.empty:
        top = ranking.iloc[0]
        findings.append(
            f"Among airlines with at least 100 flights, {top['airline'].title()} had the highest share of flights "
            f"delayed over an hour in {latest['label']} ({top['rate_over_1h']:.1%} of {int(top['total_flights']):,} flights)."
        )
    return findings
