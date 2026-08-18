import pandas as pd


def _parse_numeric(value):
    """
    Convert a raw numeric value into float.

    Invalid values such as "-", "", None, or non-numeric
    strings are converted to None.
    """

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

        if value == "-":
            return None

        value = value.replace(",", "")

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value):
    """
    Convert a raw date value into pandas Timestamp.

    Invalid or missing dates are converted to NaT.
    """

    if value is None:
        return pd.NaT

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return pd.NaT

        if value == "-":
            return pd.NaT

    return pd.to_datetime(
        value,
        errors="coerce",
    )

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

def calculate_fundamentals(
    price_data: pd.DataFrame,
    fundamental_data: pd.DataFrame,
    dividend_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine latest price, fundamental data, and dividend data,
    then calculate PE, PB, and dividend yield.

    Parameters
    ----------
    price_data : pd.DataFrame
        Latest stock prices.
        Required columns:
        - symbol
        - trade_date
        - close

    fundamental_data : pd.DataFrame
        Financial data.
        Required columns:
        - symbol
        - report_year
        - report_quarter
        - eps_ytd
        - bvps

    dividend_data : pd.DataFrame
        Dividend data.
        Required columns:
        - symbol
        - dividend_year
        - cash_dividend

    Returns
    -------
    pd.DataFrame
        Combined fundamental indicators.
    """

    price = price_data.copy()
    fundamentals = fundamental_data.copy()
    dividends = dividend_data.copy()

    # ---------------------------------------------------------
    # 1. Select the latest price for each stock
    # ---------------------------------------------------------
    price["trade_date"] = pd.to_datetime(
        price["trade_date"],
        errors="coerce",
    )

    price = (
        price.sort_values(["symbol", "trade_date"])
        .drop_duplicates(
            subset=["symbol"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 2. Select the latest financial report for each stock
    # ---------------------------------------------------------
    fundamentals = (
        fundamentals.sort_values(
            ["symbol", "report_year", "report_quarter"]
        )
        .drop_duplicates(
            subset=["symbol"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 3. Select the latest dividend record for each stock
    # ---------------------------------------------------------
    dividends = (
        dividends.sort_values(
            ["symbol", "dividend_year"]
        )
        .drop_duplicates(
            subset=["symbol"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 4. Merge price + financial data
    # ---------------------------------------------------------
    result = price.merge(
        fundamentals[
            [
                "symbol",
                "report_year",
                "report_quarter",
                "eps_ytd",
                "bvps",
            ]
        ],
        on="symbol",
        how="left",
    )

    # ---------------------------------------------------------
    # 5. Merge dividend data
    # ---------------------------------------------------------
    result = result.merge(
        dividends[
            [
                "symbol",
                "dividend_year",
                "cash_dividend",
            ]
        ],
        on="symbol",
        how="left",
    )

    # Rename DPS field
    result = result.rename(
        columns={
            "cash_dividend": "dps",
        }
    )

    # ---------------------------------------------------------
    # 6. Calculate valuation indicators
    # ---------------------------------------------------------
    result["pe"] = result.apply(
        lambda row: calculate_pe(
            row["close"],
            row["eps_ytd"],
        ),
        axis=1,
    )

    result["pb"] = result.apply(
        lambda row: calculate_pb(
            row["close"],
            row["bvps"],
        ),
        axis=1,
    )

    result["dividend_yield"] = result.apply(
        lambda row: calculate_dividend_yield(
            row["close"],
            row["dps"],
        ),
        axis=1,
    )

    return result.reset_index(drop=True)
