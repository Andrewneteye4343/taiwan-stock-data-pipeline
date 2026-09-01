"""股利資料管線。

資料來源說明（v2.0 起）：
- MOPS（公開資訊觀測站）有反爬蟲機制（FOR SECURITY REASONS），
  無法以 requests 直接抓取，需瀏覽器自動化（如 Playwright）——列為未來工作。
- 股利資料為年頻率且稀疏，v2.0 提供穩健的 CSV 匯入管線：

    python -m src.cli dividend --csv data/dividends.csv

CSV 欄位（與 dividend_data 表一致）：
    symbol, dividend_year, cash_dividend, ex_dividend_date, payment_date
"""

import csv
from pathlib import Path

import pandas as pd

from src.collector.dividend_data import parse_dividend_data
from src.config.stock_config import get_enabled_symbols
from src.etl.load import load_dividend_data
from src.etl.validate import validate_dividend_data

DEFAULT_CSV_PATH = Path("data/dividends.csv")


def read_dividend_csv(
    csv_path: Path,
) -> list[dict]:
    """
    Read dividend records from a CSV file.

    Expected columns:
        symbol, dividend_year, cash_dividend,
        ex_dividend_date, payment_date
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dividend CSV not found: {csv_path}"
        )

    records = []

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if not row.get("symbol"):
                continue

            records.append(
                {
                    "symbol": str(row["symbol"]).strip(),
                    "dividend_year": row.get(
                        "dividend_year"
                    ),
                    "cash_dividend": row.get(
                        "cash_dividend"
                    ),
                    "ex_dividend_date": row.get(
                        "ex_dividend_date"
                    ),
                    "payment_date": row.get(
                        "payment_date"
                    ),
                }
            )

    return records


def run(
    symbol: str | None = None,
    csv_path: Path | None = None,
    db_engine=None,
) -> int:
    """
    Execute the dividend data pipeline.

    Parameters
    ----------
    symbol : str | None
        Only import records for this symbol.

    csv_path : Path | None
        CSV file path.
        Defaults to data/dividends.csv.

    Returns
    -------
    int
        Total processed records.
    """

    if csv_path is None:
        csv_path = DEFAULT_CSV_PATH

    print(
        "Starting Dividend Pipeline..."
    )

    print(
        f"CSV source: {csv_path}"
    )

    raw_records = read_dividend_csv(csv_path)

    if symbol:

        raw_records = [
            record
            for record in raw_records
            if record["symbol"] == str(symbol)
        ]

    else:

        enabled = set(
            get_enabled_symbols()
        )

        raw_records = [
            record
            for record in raw_records
            if record["symbol"] in enabled
        ]

    if not raw_records:

        print(
            "No dividend records to process."
        )

        return 0

    df = parse_dividend_data(raw_records)

    print(
        f"Parsed dividend records: {len(df)}"
    )

    validate_dividend_data(df)

    processed_count = load_dividend_data(
        df,
        db_engine=db_engine,
    )

    print(
        f"Successfully processed "
        f"{processed_count} dividend records."
    )

    return processed_count
