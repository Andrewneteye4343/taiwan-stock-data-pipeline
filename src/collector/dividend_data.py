import pandas as pd

from src.collector.parsing import parse_date as _parse_date
from src.collector.parsing import parse_numeric as _parse_numeric

def parse_dividend_data(
    raw_data: list[dict],
) -> pd.DataFrame:
    """
    Parse raw dividend data.

    Required fields:
    - symbol
    - dividend_year

    Optional fields:
    - cash_dividend
    - ex_dividend_date
    - payment_date
    """

    records = []

    for item in raw_data:
        if "symbol" not in item:
            raise ValueError("Missing required field: symbol")

        if "dividend_year" not in item:
            raise ValueError("Missing required field: dividend_year")

        records.append(
            {
                "symbol": str(item["symbol"]),
                "dividend_year": int(item["dividend_year"]),
                "cash_dividend": _parse_numeric(
                    item.get("cash_dividend")
                ),
                "ex_dividend_date": _parse_date(
                    item.get("ex_dividend_date")
                ),
                "payment_date": _parse_date(
                    item.get("payment_date")
                ),
            }
        )

    result = pd.DataFrame(
        records,
        columns=[
            "symbol",
            "dividend_year",
            "cash_dividend",
            "ex_dividend_date",
            "payment_date",
        ],
    )

    result = result.drop_duplicates(
        subset=["symbol", "dividend_year"],
        keep="last",
    )

    result = result.sort_values(
        ["symbol", "dividend_year"]
    ).reset_index(drop=True)

    return result
