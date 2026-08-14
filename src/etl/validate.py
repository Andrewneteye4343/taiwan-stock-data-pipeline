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