import pandas as pd

from src.database.query import (
    get_latest_dividend_data,
    get_latest_fundamental_data,
)

from src.indicators.fundamental import calculate_fundamentals


def calculate_latest_fundamentals(
    symbol: str,
) -> pd.DataFrame:

    fundamental_data = get_latest_fundamental_data(symbol)

    if fundamental_data.empty:
        return pd.DataFrame()

    dividend_data = get_latest_dividend_data(symbol)

    result = fundamental_data.copy()

    if not dividend_data.empty:
        result = result.merge(
            dividend_data[
                [
                    "symbol",
                    "dividend_year",
                    "cash_dividend",
                ]
            ],
            on="symbol",
            how="left",
        )
    else:
        result["dividend_year"] = pd.NA
        result["cash_dividend"] = pd.NA

    result["dps"] = result["cash_dividend"]

    result = calculate_fundamentals(result)

    return result