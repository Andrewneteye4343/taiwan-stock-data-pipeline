import pandas as pd


def calculate_pe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate price-to-earnings ratio (PE).

    PE = close / EPS

    Only positive EPS values produce a valid PE.
    """

    result = df.copy()

    result["pe"] = pd.NA

    valid_eps = (
        result["eps"].notna()
        & (result["eps"] > 0)
        & result["close"].notna()
        & (result["close"] > 0)
    )

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

    PB = close / BVPS

    Only positive BVPS values produce a valid PB.
    """

    result = df.copy()

    result["pb"] = pd.NA

    valid_bvps = (
        result["bvps"].notna()
        & (result["bvps"] > 0)
        & result["close"].notna()
        & (result["close"] > 0)
    )

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

    Dividend Yield = DPS / Close * 100
    """

    result = df.copy()

    result["dividend_yield"] = pd.NA

    valid_data = (
        result["dps"].notna()
        & result["close"].notna()
        & (result["close"] > 0)
    )

    result.loc[valid_data, "dividend_yield"] = (
        result.loc[valid_data, "dps"]
        / result.loc[valid_data, "close"]
        * 100
    )

    result["dividend_yield"] = pd.to_numeric(
        result["dividend_yield"],
        errors="coerce",
    )

    return result


def calculate_gross_margin(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate gross profit margin.

    Gross Margin = gross_profit / revenue * 100
    """

    result = df.copy()

    result["gross_margin"] = pd.NA

    valid_data = (
        result["revenue"].notna()
        & (result["revenue"] != 0)
        & result["gross_profit"].notna()
    )

    result.loc[valid_data, "gross_margin"] = (
        result.loc[valid_data, "gross_profit"]
        / result.loc[valid_data, "revenue"]
        * 100
    )

    result["gross_margin"] = pd.to_numeric(
        result["gross_margin"],
        errors="coerce",
    )

    return result


def calculate_operating_margin(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate operating profit margin.

    Operating Margin = operating_income / revenue * 100
    """

    result = df.copy()

    result["operating_margin"] = pd.NA

    valid_data = (
        result["revenue"].notna()
        & (result["revenue"] != 0)
        & result["operating_income"].notna()
    )

    result.loc[valid_data, "operating_margin"] = (
        result.loc[valid_data, "operating_income"]
        / result.loc[valid_data, "revenue"]
        * 100
    )

    result["operating_margin"] = pd.to_numeric(
        result["operating_margin"],
        errors="coerce",
    )

    return result


def calculate_net_margin(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate net profit margin.

    Net Margin = net_income / revenue * 100
    """

    result = df.copy()

    result["net_margin"] = pd.NA

    valid_data = (
        result["revenue"].notna()
        & (result["revenue"] != 0)
        & result["net_income"].notna()
    )

    result.loc[valid_data, "net_margin"] = (
        result.loc[valid_data, "net_income"]
        / result.loc[valid_data, "revenue"]
        * 100
    )

    result["net_margin"] = pd.to_numeric(
        result["net_margin"],
        errors="coerce",
    )

    return result


def calculate_fundamentals(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate core fundamental indicators.

    Supported indicators:
    - PE
    - PB
    - Dividend Yield
    """

    result = df.copy()

    result = calculate_pe(result)

    result = calculate_pb(result)

    result = calculate_dividend_yield(result)

    return result