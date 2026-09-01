import pandas as pd


def _eps_column(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Return a numeric EPS column, or an all-NaN float64 series.
    """

    if column in df.columns:

        return pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return pd.Series(
        index=df.index,
        dtype="float64",
    )


def _select_eps(df: pd.DataFrame):
    """選取 PE 計算用的 EPS 基準（統一量化標準）。

    優先序：eps_ttm（近四季累計）> eps_ytd（累計）> eps（單季）。

    採用「逐列遞補」：某列 TTM 不足四季（NaN）時，
    自動退回該列的 eps_ytd；仍缺則退回 eps。
    """

    eps_ttm = _eps_column(df, "eps_ttm")

    eps_ytd = _eps_column(df, "eps_ytd")

    eps = _eps_column(df, "eps")

    selected = (
        eps_ttm
        .fillna(eps_ytd)
        .fillna(eps)
    )

    if selected.isna().all():
        raise ValueError(
            "PE requires one of: eps_ttm, eps_ytd, eps"
        )

    return selected


def calculate_pe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate price-to-earnings ratio (PE).

    PE = close / EPS

    依 _select_eps 的優先序選取 EPS 基準（預設 TTM EPS）。
    只有正數 EPS 才計算 PE。
    """

    result = df.copy()

    result["pe"] = pd.NA

    eps = _select_eps(result)

    # PostgreSQL NUMERIC 欄位讀回為 Decimal，
    # 統一轉為 float 再做除法（避免 Decimal/float 型別錯誤）
    close = pd.to_numeric(
        result["close"],
        errors="coerce",
    )

    valid_eps = (
        eps.notna()
        & (eps > 0)
        & close.notna()
        & (close > 0)
    )

    result.loc[valid_eps, "pe"] = (
        close[valid_eps]
        / eps[valid_eps]
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

    bvps = pd.to_numeric(
        result["bvps"],
        errors="coerce",
    )

    close = pd.to_numeric(
        result["close"],
        errors="coerce",
    )

    valid_bvps = (
        bvps.notna()
        & (bvps > 0)
        & close.notna()
        & (close > 0)
    )

    result.loc[valid_bvps, "pb"] = (
        close[valid_bvps]
        / bvps[valid_bvps]
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

    dps = pd.to_numeric(
        result["dps"],
        errors="coerce",
    )

    close = pd.to_numeric(
        result["close"],
        errors="coerce",
    )

    valid_data = (
        dps.notna()
        & close.notna()
        & (close > 0)
    )

    result.loc[valid_data, "dividend_yield"] = (
        dps[valid_data]
        / close[valid_data]
        * 100
    )

    result["dividend_yield"] = pd.to_numeric(
        result["dividend_yield"],
        errors="coerce",
    )

    return result


def calculate_ttm_eps(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """計算「近四季累計 EPS」（Trailing Twelve Months）。

    統一量化標準：PE 一律以 TTM EPS 為基準（市場慣例），
    避免「單季 EPS」與「累計 EPS」混用的不一致。

    Parameters
    ----------
    df : pd.DataFrame
        歷史季報資料，需含欄位：
        - symbol
        - report_year
        - report_quarter
        - eps（單季 EPS）

    回傳
    ----
    pd.DataFrame
        新增欄位 ttm_eps：
        - 累計滿 4 季時 = 最近四季單季 EPS 加總
        - 不足 4 季時 = NaN（資料不足，不硬算）
    """

    result = df.copy()

    if result.empty:
        result["ttm_eps"] = pd.NA
        return result

    required = {
        "symbol",
        "report_year",
        "report_quarter",
        "eps",
    }

    missing = required - set(result.columns)

    if missing:
        raise ValueError(
            f"TTM EPS requires columns: {missing}"
        )

    result = result.sort_values(
        ["symbol", "report_year", "report_quarter"]
    )

    result["ttm_eps"] = pd.NA

    for symbol, group in result.groupby("symbol"):

        # 依時間排序後，取最近四季的單季 EPS 加總
        group = group.sort_values(
            ["report_year", "report_quarter"]
        )

        eps_values = group["eps"]

        ttm = (
            eps_values
            .rolling(window=4, min_periods=4)
            .sum()
        )

        result.loc[group.index, "ttm_eps"] = ttm

    result["ttm_eps"] = pd.to_numeric(
        result["ttm_eps"],
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
    - PE（EPS 基準優先序：eps_ttm > eps_ytd > eps）
    - PB
    - Dividend Yield
    - Gross Margin / Operating Margin / Net Margin（有損益表欄位時）
    """

    result = df.copy()

    result = calculate_pe(result)

    result = calculate_pb(result)

    result = calculate_dividend_yield(result)

    if (
        "revenue" in result.columns
        and "gross_profit" in result.columns
    ):
        result = calculate_gross_margin(result)

    if (
        "revenue" in result.columns
        and "operating_income" in result.columns
    ):
        result = calculate_operating_margin(result)

    if (
        "revenue" in result.columns
        and "net_income" in result.columns
    ):
        result = calculate_net_margin(result)

    return result