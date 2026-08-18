import pandas as pd

from src.database.query import get_latest_fundamental_data
from src.indicators.fundamental import calculate_fundamentals


def calculate_latest_fundamentals(
    symbol: str,
) -> pd.DataFrame:
    """
    Get the latest price and fundamental data for a stock
    and calculate fundamental indicators.

    Parameters
    ----------
    symbol : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the latest fundamental data
        and calculated indicators.

        Returns an empty DataFrame when no complete
        fundamental data is available.
    """

    df = get_latest_fundamental_data(symbol)

    if df.empty:
        return df

    required_columns = {
        "close",
        "eps",
        "bvps",
        "dps",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing fundamental columns: {missing_columns}"
        )

    result = calculate_fundamentals(df)

    return result