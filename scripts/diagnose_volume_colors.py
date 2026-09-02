"""診斷成交量圖 bar 顏色（v2.2.1 除錯用）。

用法（不需重新 build）：
    docker compose cp scripts/diagnose_volume_colors.py dashboard:/app/scripts/
    docker compose exec dashboard python scripts/diagnose_volume_colors.py
"""

import os

import pandas as pd

from sqlalchemy import create_engine

engine = create_engine(os.environ["DATABASE_URL"])

df = pd.read_sql(
    "SELECT dp.trade_date, dp.volume "
    "FROM daily_price dp "
    "JOIN stock_master sm ON sm.stock_id = dp.stock_id "
    "WHERE sm.symbol = '2330' ORDER BY dp.trade_date",
    engine,
)

df["volume"] = pd.to_numeric(
    df["volume"],
    errors="coerce",
)

df["previous_volume"] = df["volume"].shift(1)


def get_volume_color(row):
    """
    Determine volume bar color.
    """

    if pd.isna(row["previous_volume"]):
        return "#FFFFFF"

    if row["volume"] > row["previous_volume"]:
        return "#FF5252"

    if row["volume"] < row["previous_volume"]:
        return "#2ECC71"

    return "#FFFFFF"


df["color"] = df.apply(
    get_volume_color,
    axis=1,
)

print("=== 2330 最近 15 個交易日的成交量與顏色 ===")
print(df.tail(15).to_string())
print()
print("=== 顏色統計（期望：白/紅/綠混合）===")
print(df["color"].value_counts().to_string())
