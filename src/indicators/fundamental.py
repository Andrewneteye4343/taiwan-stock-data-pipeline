import pandas as pd


def calculate_pe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate price-to-earnings ratio (PE).

    PE is calculated as:

        PE = close / EPS

    Only positive EPS values produce a valid PE.
    EPS values that are zero or negative are treated
    as invalid and result in NaN.
    """

    result = df.copy()

    result["pe"] = pd.NA

    valid_eps = result["eps"] > 0

    result.loc[valid_eps, "pe"] = (
        result.loc[valid_eps, "close"]
        / result.loc[valid_eps, "eps"]
    )

    result["pe"] = pd.to_numeric(
        result["pe"],
        errors="coerce",
    )

    return result


def calculate_pb(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate price-to-book ratio (PB).

    PB is calculated as:

        PB = close / BVPS

    Only positive BVPS values produce a valid PB.
    BVPS values that are zero or negative are treated
    as invalid and result in NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Stock price and fundamental data.

        Required columns:
        - close
        - bvps

    Returns
    -------
    pd.DataFrame
        DataFrame with an additional pb column.
    """

    result = df.copy()

    result["pb"] = pd.NA

    valid_bvps = result["bvps"] > 0

    result.loc[valid_bvps, "pb"] = (
        result.loc[valid_bvps, "close"]
        / result.loc[valid_bvps, "bvps"]
    )

    result["pb"] = pd.to_numeric(
        result["pb"],
        errors="coerce",
    )

    return result

def calculate_dividend_yield(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate dividend yield.

    Dividend yield is calculated as:

        Dividend Yield = DPS / Close * 100

    Only positive close prices produce a valid
    dividend yield.

    DPS equal to zero is valid and produces
    a dividend yield of zero.

    Parameters
    ----------
    df : pd.DataFrame
        Stock price and fundamental data.

        Required columns:
        - close
        - dps

    Returns
    -------
    pd.DataFrame
        DataFrame with an additional
        dividend_yield column.
    """

    result = df.copy()

    result["dividend_yield"] = pd.NA

    valid_close = result["close"] > 0

    result.loc[valid_close, "dividend_yield"] = (
        result.loc[valid_close, "dps"]
        / result.loc[valid_close, "close"]
        * 100
    )

    result["dividend_yield"] = pd.to_numeric(
        result["dividend_yield"],
        errors="coerce",
    )

    return result

def calculate_fundamentals(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate all supported fundamental indicators.

    Currently supported indicators:
    - PE
    - PB
    - Dividend Yield

    Parameters
    ----------
    df : pd.DataFrame
        Stock price and fundamental data.

        Required columns:
        - close
        - eps
        - bvps
        - dps

    Returns
    -------
    pd.DataFrame
        DataFrame containing:
        - pe
        - pb
        - dividend_yield
    """

    result = df.copy()

    result = calculate_pe(result)

    result = calculate_pb(result)

    result = calculate_dividend_yield(result)

    return result