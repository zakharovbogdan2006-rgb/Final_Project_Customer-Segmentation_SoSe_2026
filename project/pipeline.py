"""Reproducible RFM segmentation pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

REQUIRED = {"CustomerID", "DAYSSINCELASTORDER", "TOTAL_ORDERS", "REVENUE"}


def make_demo_data(rows: int = 240, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "CustomerID": np.arange(10_000, 10_000 + rows),
        "DAYSSINCELASTORDER": rng.integers(1, 365, rows),
        "TOTAL_ORDERS": rng.poisson(7, rows) + 1,
        "REVENUE": np.round(rng.gamma(3, 180, rows), 2),
    })


def load_and_clean(path: Path | None, demo: bool) -> pd.DataFrame:
    data = make_demo_data() if demo else pd.read_csv(path)
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(sorted(missing))}")
    result = data.copy()
    for column in REQUIRED - {"CustomerID"}:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = result.dropna(subset=REQUIRED).drop_duplicates(subset="CustomerID")
    result = result[(result.DAYSSINCELASTORDER >= 0) & (result.TOTAL_ORDERS >= 0) & (result.REVENUE >= 0)]
    if len(result) < 8:
        raise ValueError("At least eight valid customers are required for four segments")
    return result.reset_index(drop=True)


def segment(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = data.copy()
    result["Recency"] = pd.qcut(result.DAYSSINCELASTORDER.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    result["Frequency"] = pd.qcut(result.TOTAL_ORDERS.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    result["Monetary"] = pd.qcut(result.REVENUE.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    features = ["Recency", "Frequency", "Monetary"]
    scaled = StandardScaler().fit_transform(result[features])
    result["Cluster"] = KMeans(n_clusters=4, random_state=42, n_init=50).fit_predict(scaled)
    profiles = result.groupby("Cluster", as_index=False).agg(
        Customers=("CustomerID", "count"), Avg_recency_days=("DAYSSINCELASTORDER", "mean"),
        Avg_orders=("TOTAL_ORDERS", "mean"), Avg_revenue=("REVENUE", "mean"),
    )
    return result, profiles


def write_report(customers: pd.DataFrame, profiles: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    customers.to_csv(output / "customer_segments.csv", index=False)
    profiles.round(2).to_csv(output / "segment_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(customers["DAYSSINCELASTORDER"], customers["REVENUE"], c=customers["Cluster"], cmap="viridis", alpha=.7)
    ax.set(xlabel="Days since last order", ylabel="Revenue", title="Customer segments (RFM clustering)")
    fig.tight_layout()
    fig.savefig(output / "segments.png", dpi=160)
    plt.close(fig)
    (output / "README.md").write_text("# Results\n\nClusters are descriptive RFM segments, not validated churn predictions.\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create reproducible RFM customer segments")
    parser.add_argument("--input", type=Path, help="CSV with CustomerID, DAYSSINCELASTORDER, TOTAL_ORDERS and REVENUE")
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--generate-demo", action="store_true", help="Use a deterministic synthetic dataset")
    args = parser.parse_args()
    if not args.generate_demo and args.input is None:
        parser.error("provide --input FILE or use --generate-demo")
    customers, profiles = segment(load_and_clean(args.input, args.generate_demo))
    write_report(customers, profiles, args.output)
    print(profiles.round(2).to_string(index=False))
    print(f"Saved reproducible outputs to {args.output}")


if __name__ == "__main__":
    main()
