import pandas as pd

from src.pipelines.dividend import read_dividend_csv


def test_read_dividend_csv(tmp_path):

    csv_path = tmp_path / "dividends.csv"

    csv_path.write_text(
        "symbol,dividend_year,cash_dividend,ex_dividend_date,payment_date\n"
        "2330,2026,5.00,2026-07-01,2026-07-31\n"
        "2317,2026,3.50,2026-08-01,2026-08-31\n"
        ",2026,1.00,,\n",
        encoding="utf-8",
    )

    records = read_dividend_csv(csv_path)

    # 缺少 symbol 的列應被跳過
    assert len(records) == 2

    assert records[0]["symbol"] == "2330"

    assert records[1]["symbol"] == "2317"


def test_read_dividend_csv_missing_file(tmp_path):

    missing = tmp_path / "nope.csv"

    try:

        read_dividend_csv(missing)

        assert False, "應拋出 FileNotFoundError"

    except FileNotFoundError:
        pass
