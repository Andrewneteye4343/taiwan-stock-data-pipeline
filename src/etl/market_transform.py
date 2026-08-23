import pandas as pd


def prepare_market_data(
    records: list[dict],
    stocks: list[dict],
) -> pd.DataFrame:
    """
    Convert collected market records into a
    standardized DataFrame with stock metadata.

    Parameters
    ----------
    records : list[dict]
        Raw market records collected from TWSE.

    stocks : list[dict]
        Stock configurations loaded from stocks.yaml.

    Returns
    -------
    pd.DataFrame
        Market data enriched with:
        - symbol
        - market
        - industry

    Raises
    ------
    ValueError
        If records are empty.
    """

    if not records:

        raise ValueError(
            "No market records provided."
        )

    # ----------------------------------------
    # Convert market records to DataFrame
    # ----------------------------------------

    df = pd.DataFrame(
        records
    )

    if df.empty:

        raise ValueError(
            "Market records produced "
            "an empty DataFrame."
        )

    # ----------------------------------------
    # Build stock metadata
    # ----------------------------------------

    stock_metadata = pd.DataFrame(
        stocks
    )

    required_metadata_columns = [
        "symbol",
        "market",
        "industry",
    ]

    missing_columns = [
        column
        for column in required_metadata_columns
        if column not in stock_metadata.columns
    ]

    if missing_columns:

        raise ValueError(
            "Stock configuration is missing "
            f"required fields: "
            f"{', '.join(missing_columns)}"
        )

    # ----------------------------------------
    # Merge stock metadata
    # ----------------------------------------

    df = df.merge(
        stock_metadata[
            required_metadata_columns
        ],
        on="symbol",
        how="left",
    )

    return df