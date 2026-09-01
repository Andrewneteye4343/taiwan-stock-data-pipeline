import pandas as pd

from src.database.connection import engine


def derive_single_quarter_eps(
    df: pd.DataFrame,
    db_engine=None,
) -> pd.DataFrame:
    """
    由累計 EPS（eps_ytd）推導單季 EPS（eps）。

    TWSE 損益表為「累計數」（Q2 顯示上半年累計），
    單季 EPS 需以差值推導：

        單季 EPS(Qn) = 累計 EPS(Qn) − 累計 EPS(Qn-1)

    規則：
    - Q1：單季 = 累計（年初至今即當季）
    - Q2-Q4：需前一季累計值（優先查同批次 df，其次查資料庫）
    - 前一季資料不存在 → eps 保持 None（由 PE 遞補鏈處理）

    Parameters
    ----------
    df : pd.DataFrame
        財報資料，需含 symbol / report_year / report_quarter / eps_ytd。

    db_engine : SQLAlchemy Engine, optional
        用於查詢前一季累計 EPS。

    Returns
    -------
    pd.DataFrame
        填入單季 eps 的資料。
    """

    result = df.copy()

    if df.empty:
        return result

    if "eps_ytd" not in result.columns:
        return result

    result["eps"] = None

    for index, row in result.iterrows():

        ytd = row.get("eps_ytd")

        if pd.isna(ytd):
            continue

        quarter = int(row["report_quarter"])

        if quarter == 1:

            result.at[index, "eps"] = ytd

            continue

        previous_ytd = _get_previous_quarter_eps_ytd(
            row,
            result,
            db_engine=db_engine,
        )

        if previous_ytd is not None:

            result.at[index, "eps"] = (
                float(ytd) - float(previous_ytd)
            )

    result["eps"] = pd.to_numeric(
        result["eps"],
        errors="coerce",
    )

    return result


def _get_previous_quarter_eps_ytd(
    row,
    df: pd.DataFrame,
    db_engine=None,
):
    """
    Find the previous quarter's cumulative EPS (eps_ytd).

    Priority: same batch (df) > database.
    """

    symbol = row["symbol"]
    year = int(row["report_year"])
    quarter = int(row["report_quarter"])

    previous_year = year
    previous_quarter = quarter - 1

    if previous_quarter == 0:
        previous_quarter = 4
        previous_year = year - 1

    # 1. Same batch
    same_batch = df[
        (df["symbol"] == symbol)
        & (df["report_year"] == previous_year)
        & (df["report_quarter"] == previous_quarter)
    ]

    if not same_batch.empty:

        value = same_batch.iloc[0].get("eps_ytd")

        if not pd.isna(value):
            return value

    # 2. Database
    if db_engine is None:
        db_engine = engine

    from sqlalchemy import text

    query = text(
        """
        SELECT fd.eps_ytd
        FROM fundamental_data fd
        JOIN stock_master sm
            ON fd.stock_id = sm.stock_id
        WHERE sm.symbol = :symbol
          AND fd.report_year = :year
          AND fd.report_quarter = :quarter;
        """
    )

    with db_engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "symbol": symbol,
                "year": previous_year,
                "quarter": previous_quarter,
            },
        )

        row_result = result.fetchone()

    if row_result is None:
        return None

    return row_result.eps_ytd


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