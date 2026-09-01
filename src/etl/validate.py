import pandas as pd


def validate_daily_price(df: pd.DataFrame) -> None:
    """
    Validate transformed daily stock price data.

    Raises
    ------
    ValueError
        If any data quality rule is violated.
    """

    # 1. Required columns
    required_columns = {
        "symbol",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Missing values
    if df[list(required_columns)].isnull().any().any():
        raise ValueError(
            "Data contains NULL / missing values."
        )

    # 3. Price must be positive
    price_columns = [
        "open",
        "high",
        "low",
        "close",
    ]

    if (df[price_columns] <= 0).any().any():
        raise ValueError(
            "Stock price must be greater than zero."
        )

    # 4. High must be >= Low
    if (df["high"] < df["low"]).any():
        raise ValueError(
            "High price cannot be lower than low price."
        )

    # 5. Volume must not be negative
    if (df["volume"] < 0).any():
        raise ValueError(
            "Volume cannot be negative."
        )

    # 6. Turnover must not be negative
    if (df["turnover"] < 0).any():
        raise ValueError(
            "Turnover cannot be negative."
        )

    # 7. Duplicate stock/date
    duplicated = df.duplicated(
        subset=["symbol", "trade_date"],
        keep=False,
    )

    if duplicated.any():
        raise ValueError(
            "Duplicate stock/date records detected."
        )

    print("Data validation passed.")


def validate_fundamental_data(df: pd.DataFrame) -> None:
    """
    Validate quarterly fundamental data.

    Raises
    ------
    ValueError
        If any data quality rule is violated.
    """

    required_columns = {
        "symbol",
        "report_year",
        "report_quarter",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError(
            "Fundamental data is empty."
        )

    # 1. Report quarter must be 1-4
    invalid_quarter = (
        ~df["report_quarter"].isin([1, 2, 3, 4])
    )

    if invalid_quarter.any():
        raise ValueError(
            "report_quarter must be in (1, 2, 3, 4)."
        )

    # 2. Report year must be plausible (民國 100 年以後)
    invalid_year = df["report_year"] < 2011

    if invalid_year.any():
        raise ValueError(
            "report_year must be >= 2011."
        )

    # 3. Duplicate stock / quarter
    duplicated = df.duplicated(
        subset=["symbol", "report_year", "report_quarter"],
        keep=False,
    )

    if duplicated.any():
        raise ValueError(
            "Duplicate stock/quarter records detected."
        )

    # 4. BVPS must not be negative when present
    if "bvps" in df.columns:

        negative_bvps = (
            df["bvps"].notna()
            & (df["bvps"] < 0)
        )

        if negative_bvps.any():
            raise ValueError(
                "BVPS cannot be negative."
            )

    print("Fundamental data validation passed.")


def validate_dividend_data(df: pd.DataFrame) -> None:
    """
    Validate dividend data.

    Raises
    ------
    ValueError
        If any data quality rule is violated.
    """

    required_columns = {
        "symbol",
        "dividend_year",
        "cash_dividend",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError(
            "Dividend data is empty."
        )

    # 1. Cash dividend must not be negative
    negative_dividend = (
        df["cash_dividend"].notna()
        & (df["cash_dividend"] < 0)
    )

    if negative_dividend.any():
        raise ValueError(
            "cash_dividend cannot be negative."
        )

    # 2. Duplicate stock / dividend year
    duplicated = df.duplicated(
        subset=["symbol", "dividend_year"],
        keep=False,
    )

    if duplicated.any():
        raise ValueError(
            "Duplicate stock/dividend_year records detected."
        )

    print("Dividend data validation passed.")