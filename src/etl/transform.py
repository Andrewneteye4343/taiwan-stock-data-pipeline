import pandas as pd


def transform_daily_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw stock daily price data.

    Parameters
    ----------
    df : pd.DataFrame
        Raw daily price data.

    Returns
    -------
    pd.DataFrame
        Transformed daily price data.
    """

    df = df.copy()

    # ----------------------------------------
    # Required columns
    # ----------------------------------------

    required_columns = [
        "symbol",
        "name",
        "market",
        "industry",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Keep required columns
    df = df[required_columns].copy()

    # ----------------------------------------
    # Convert trade date
    # ----------------------------------------

    df["trade_date"] = pd.to_datetime(
        df["trade_date"],
        errors="coerce",
    )

    # ----------------------------------------
    # Convert numeric columns
    # ----------------------------------------

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # ----------------------------------------
    # Clean string columns
    # ----------------------------------------

    string_columns = [
        "symbol",
        "name",
        "market",
        "industry",
    ]

    for column in string_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # ----------------------------------------
    # Sort data
    # ----------------------------------------

    df = df.sort_values(
        ["symbol", "trade_date"],
        ascending=[True, False],
    )

    # ----------------------------------------
    # Reset index
    # ----------------------------------------

    df = df.reset_index(drop=True)

    return df