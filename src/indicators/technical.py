import pandas as pd


def calculate_price_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily price change and percentage change.

    Calculations are performed independently for each stock symbol.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    Returns
    -------
    pd.DataFrame
        DataFrame with:
        - change
        - change_pct
    """

    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    result["change"] = (
        result.groupby("symbol")["close"]
        .diff()
    )

    result["change_pct"] = (
        result.groupby("symbol")["close"]
        .pct_change()
        * 100
    )

    return result


def calculate_volume_ratio(
    df: pd.DataFrame,
    window: int = 20,
) -> pd.DataFrame:
    """
    Calculate volume ratio.

    Volume ratio is defined as:

        current volume /
        rolling average volume

    The calculation is performed independently
    for each stock symbol.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    window : int
        Rolling average window.

    Returns
    -------
    pd.DataFrame
        DataFrame with volume_ratio column.
    """

    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    result["average_volume"] = (
        result.groupby("symbol")["volume"]
        .transform(
            lambda series:
            series.rolling(
                window=window,
                min_periods=1,
            ).mean()
        )
    )

    result["volume_ratio"] = (
        result["volume"]
        / result["average_volume"]
    )

    return result

def calculate_moving_average(
    df: pd.DataFrame,
    window: int,
) -> pd.DataFrame:
    """
    Calculate simple moving average (SMA).

    The calculation is performed independently
    for each stock symbol.

    A moving average is only calculated when
    enough historical observations are available.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    window : int
        Number of trading days used for the
        moving average.

    Returns
    -------
    pd.DataFrame
        DataFrame with an additional MA column.
    """

    if window <= 0:
        raise ValueError(
            "window must be greater than 0"
        )

    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    column_name = f"ma{window}"

    result[column_name] = (
        result.groupby("symbol")["close"]
        .transform(
            lambda series:
            series.rolling(
                window=window,
                min_periods=window,
            ).mean()
        )
    )

    return result

def calculate_moving_averages(
    df: pd.DataFrame,
    windows: list[int] = [5, 20, 60],
) -> pd.DataFrame:
    """
    Calculate multiple simple moving averages.

    The calculation is performed independently
    for each stock symbol.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    windows : list[int]
        Moving average windows.

    Returns
    -------
    pd.DataFrame
        DataFrame with MA columns such as:
        ma5, ma20, ma60.
    """

    result = df.copy()

    for window in windows:

        result = calculate_moving_average(
            result,
            window=window,
        )

    return result

def calculate_kd(
    df: pd.DataFrame,
    window: int = 9,
) -> pd.DataFrame:
    """
    Calculate stochastic KD indicators.

    RSV is calculated from the highest high and lowest low
    over the specified rolling window.

    K and D are calculated using the standard 2/3 and 1/3
    smoothing method.

    The calculation is performed independently for each
    stock symbol.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    window : int
        Lookback period for RSV.

    Returns
    -------
    pd.DataFrame
        DataFrame with:
        - rsv
        - k
        - d
    """

    if window <= 0:
        raise ValueError(
            "window must be greater than 0"
        )

    required_columns = {
        "symbol",
        "trade_date",
        "high",
        "low",
        "close",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    result["highest_high"] = (
        result.groupby("symbol")["high"]
        .transform(
            lambda series:
            series.rolling(
                window=window,
                min_periods=window,
            ).max()
        )
    )

    result["lowest_low"] = (
        result.groupby("symbol")["low"]
        .transform(
            lambda series:
            series.rolling(
                window=window,
                min_periods=window,
            ).min()
        )
    )

    price_range = (
        result["highest_high"]
        - result["lowest_low"]
    )

    result["rsv"] = (
        (
            result["close"]
            - result["lowest_low"]
        )
        / price_range
        * 100
    )

    result["k"] = pd.NA
    result["d"] = pd.NA

    for symbol, group in result.groupby(
        "symbol",
        sort=False,
    ):
        k_value = 50.0
        d_value = 50.0

        for index in group.index:

            rsv = result.at[index, "rsv"]

            if pd.isna(rsv):
                continue

            k_value = (
                2 / 3 * k_value
                + 1 / 3 * float(rsv)
            )

            d_value = (
                2 / 3 * d_value
                + 1 / 3 * k_value
            )

            result.at[index, "k"] = k_value
            result.at[index, "d"] = d_value

    return result

def calculate_rsi(
    df: pd.DataFrame,
    window: int,
) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI).

    RSI is calculated independently for each stock symbol.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    window : int
        RSI calculation period.

    Returns
    -------
    pd.DataFrame
        DataFrame with an additional rsi{window} column.
    """

    if window <= 0:
        raise ValueError(
            "window must be greater than 0"
        )

    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    column_name = f"rsi{window}"

    def calculate_group_rsi(close):
        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        average_gain = (
            gain.rolling(
                window=window,
                min_periods=window,
            ).mean()
        )

        average_loss = (
            loss.rolling(
                window=window,
                min_periods=window,
            ).mean()
        )

        rs = average_gain / average_loss

        rsi = 100 - (
            100 / (1 + rs)
        )

        return rsi

    result[column_name] = (
        result.groupby("symbol")["close"]
        .transform(calculate_group_rsi)
    )

    return result


def calculate_rsis(
    df: pd.DataFrame,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """
    Calculate multiple RSI indicators.

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    windows : list[int] | None
        RSI periods to calculate.
        Defaults to [6, 14, 21].

    Returns
    -------
    pd.DataFrame
        DataFrame with multiple RSI columns.
    """

    if windows is None:
        windows = [6, 14, 21]

    result = df.copy()

    for window in windows:
        result = calculate_rsi(
            result,
            window=window,
        )

    return result