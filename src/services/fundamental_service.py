import pandas as pd

from src.database.query import (
    get_fundamental_history as query_fundamental_history,
    get_latest_dividend_data,
    get_latest_fundamental_data,
)

from src.indicators.fundamental import (
    calculate_fundamentals,
    calculate_ttm_eps,
)


def calculate_latest_fundamentals(
    symbol: str,
    db_engine=None,
) -> pd.DataFrame:

    fundamental_data = get_latest_fundamental_data(
        symbol,
        db_engine=db_engine,
    )

    if fundamental_data.empty:
        return pd.DataFrame()

    dividend_data = get_latest_dividend_data(
        symbol,
        db_engine=db_engine,
    )

    result = fundamental_data.copy()

    if not dividend_data.empty:
        result = result.merge(
            dividend_data[
                [
                    "symbol",
                    "dividend_year",
                    "cash_dividend",
                ]
            ],
            on="symbol",
            how="left",
        )
    else:
        result["dividend_year"] = pd.NA
        result["cash_dividend"] = pd.NA

    result["dps"] = result["cash_dividend"]

    # ---------------------------------------------------------
    # 統一量化標準：PE 使用 TTM EPS（近四季累計）
    # ---------------------------------------------------------

    history = query_fundamental_history(
        symbol,
        db_engine=db_engine,
    )

    if not history.empty:

        history_with_ttm = calculate_ttm_eps(history)

        latest_ttm = (
            history_with_ttm
            .sort_values(
                ["report_year", "report_quarter"]
            )
            .iloc[-1]
        )

        result["eps_ttm"] = latest_ttm.get(
            "ttm_eps",
            pd.NA,
        )

    result = calculate_fundamentals(result)

    return result

def get_fundamental_history(
    symbol: str,
) -> pd.DataFrame:
    """
    Get historical quarterly fundamental data
    for a given stock symbol.

    Parameters
    ----------
    symbol : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Historical quarterly fundamental data.
    """

    return query_fundamental_history(symbol)