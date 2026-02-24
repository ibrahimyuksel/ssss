import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiscountFeatures:
    pct_vs_30d_avg: float
    delta_vs_competitor_median: float
    delta_vs_competitor_min: float


def heuristic_score(features: DiscountFeatures) -> float:
    """Basit ve hızlı bir skorlayıcı (0-1)."""
    score = 0.0
    if features.pct_vs_30d_avg >= 0.25:
        score += 0.45
    elif features.pct_vs_30d_avg >= 0.15:
        score += 0.30

    if features.delta_vs_competitor_median <= -0.15:
        score += 0.35
    elif features.delta_vs_competitor_median <= -0.08:
        score += 0.20

    if features.delta_vs_competitor_min <= -0.05:
        score += 0.20

    return min(score, 1.0)


def decision_from_score(score: float) -> str:
    if score >= 0.80:
        return "real_discount"
    if score >= 0.60:
        return "watch"
    return "ignore"


def init_db(db_path: Path, schema_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI destekli indirim analiz altyapısı")
    parser.add_argument("--init-db", action="store_true", help="SQLite şemasını uygular")
    parser.add_argument("--db-path", type=Path, default=Path("data/discounts.db"))
    parser.add_argument("--schema-path", type=Path, default=Path("schema.sql"))
    args = parser.parse_args()

    if args.init_db:
        init_db(args.db_path, args.schema_path)
        print(f"DB hazırlandı: {args.db_path}")
        return

    sample = DiscountFeatures(
        pct_vs_30d_avg=0.28,
        delta_vs_competitor_median=-0.19,
        delta_vs_competitor_min=-0.09,
    )
    score = heuristic_score(sample)
    decision = decision_from_score(score)
    print(f"Skor: {score:.2f} / Karar: {decision}")


if __name__ == "__main__":
    main()
