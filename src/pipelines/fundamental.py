"""季報（基本面）資料管線（由 scripts/collect_fundamental.py 遷移而來）。

統一 CLI 入口：python -m src.cli fundamental [--symbol 2330]
"""

from src.api.twse import fetch_twse_api
from src.collector.fundamental_data import (
    merge_twse_financial_and_balance_sheet,
    normalize_twse_balance_sheet_data,
    normalize_twse_financial_data,
    parse_financial_data,
)
from src.config.stock_config import (
    get_enabled_symbols,
    get_stock_config,
)
from src.etl.load import load_fundamental_data
from src.etl.validate import validate_fundamental_data


TWSE_FUNDAMENTAL_ENDPOINT = (
    "opendata/t187ap06_L_ci"
)

TWSE_BALANCE_SHEET_ENDPOINT = (
    "opendata/t187ap07_L_ci"
)


def fetch_fundamental_data():
    """
    Fetch TWSE financial and balance sheet
    data once for the whole pipeline.

    The TWSE APIs are fetched only once and
    the returned records are reused for every
    enabled stock.
    """

    print(
        "Fetching TWSE financial data..."
    )

    financial_raw = fetch_twse_api(
        TWSE_FUNDAMENTAL_ENDPOINT
    )

    print(
        "Total TWSE financial records: "
        f"{len(financial_raw)}"
    )

    print(
        "Fetching TWSE balance sheet data..."
    )

    balance_raw = fetch_twse_api(
        TWSE_BALANCE_SHEET_ENDPOINT
    )

    print(
        "Total TWSE balance sheet records: "
        f"{len(balance_raw)}"
    )

    return financial_raw, balance_raw


def process_symbol(
    symbol,
    financial_raw,
    balance_raw,
):
    """
    Process fundamental data for one stock.

    Returns
    -------
    tuple[int, str]
        processed_count, status

        status can be:
        - "success"   both financial and balance sheet exist
        - "partial"   only one of them exists
        - "no_data"   neither exists
    """

    print()
    print(
        "=" * 60
    )
    print(
        f"Processing stock: {symbol}"
    )
    print(
        "=" * 60
    )

    financial_data = [
        row
        for row in financial_raw
        if str(row.get("公司代號")) == str(symbol)
    ]

    balance_data = [
        row
        for row in balance_raw
        if str(row.get("公司代號")) == str(symbol)
    ]

    print(
        f"Financial records: "
        f"{len(financial_data)}"
    )

    print(
        f"Balance sheet records: "
        f"{len(balance_data)}"
    )

    has_financial = bool(financial_data)

    has_balance = bool(balance_data)

    if not has_financial and not has_balance:

        print(
            f"[WARNING] No fundamental data "
            f"available for {symbol}"
        )

        return 0, "no_data"

    if not has_financial:

        print(
            f"[WARNING] No financial data "
            f"found for {symbol}"
        )

    elif not has_balance:

        print(
            f"[WARNING] No balance sheet data "
            f"found for {symbol}"
        )

    normalized_financial = (
        normalize_twse_financial_data(financial_data)
        if has_financial
        else []
    )

    normalized_balance = (
        normalize_twse_balance_sheet_data(balance_data)
        if has_balance
        else []
    )

    merged_data = (
        merge_twse_financial_and_balance_sheet(
            normalized_financial,
            normalized_balance,
        )
    )

    fundamental_df = parse_financial_data(
        merged_data
    )

    print(
        "Parsed fundamental records: "
        f"{len(fundamental_df)}"
    )

    if fundamental_df.empty:

        print(
            f"[WARNING] No parsed fundamental "
            f"data for {symbol}"
        )

        return 0, "no_data"

    # 資料品質檢查（Phase 1：季務資料準確性）
    validate_fundamental_data(fundamental_df)

    processed_count = load_fundamental_data(
        fundamental_df
    )

    print(
        f"Successfully processed "
        f"{processed_count} fundamental "
        f"records for {symbol}."
    )

    if has_financial and has_balance:

        return processed_count, "success"

    return processed_count, "partial"


def run(
    symbol: str | None = None,
    db_engine=None,
) -> int:
    """
    Execute the fundamental (quarterly) data pipeline.

    Parameters
    ----------
    symbol : str | None
        Stock symbol to process.
        If None, all enabled type=stock symbols
        are processed.

    Returns
    -------
    int
        Total processed records.
    """

    print(
        "Starting TWSE Fundamental Pipeline..."
    )

    if symbol:

        stock_config = get_stock_config(symbol)

        if stock_config is None:

            raise ValueError(
                f"Symbol {symbol} "
                "is not configured in stocks.yaml."
            )

        if stock_config.get("type") != "stock":

            print(
                f"[WARNING] {symbol} has "
                f"type='{stock_config.get('type')}'."
            )

            print(
                "Fundamental Pipeline only "
                "processes type='stock'."
            )

            return 0

        symbols = [symbol]

        print(
            "Mode: single stock"
        )

    else:

        symbols = get_enabled_symbols(
            types=("stock",)
        )

        print(
            "Mode: enabled stocks from "
            "stocks.yaml"
        )

    if not symbols:

        print(
            "No enabled stocks to process."
        )

        return 0

    print(
        "Stocks to process: "
        f"{', '.join(symbols)}"
    )

    financial_raw, balance_raw = (
        fetch_fundamental_data()
    )

    total_processed = 0

    success_count = 0

    partial_count = 0

    no_data_count = 0

    no_data_symbols = []

    failed_symbols = []

    for current_symbol in symbols:

        try:

            processed_count, status = process_symbol(
                current_symbol,
                financial_raw,
                balance_raw,
            )

            total_processed += processed_count

            if status == "success":

                success_count += 1

            elif status == "partial":

                partial_count += 1

            elif status == "no_data":

                no_data_count += 1

                no_data_symbols.append(
                    current_symbol
                )

        except Exception as exc:

            print()

            print(
                f"[ERROR] Failed to process "
                f"{current_symbol}: {exc}"
            )

            failed_symbols.append(
                current_symbol
            )

    print()
    print(
        "=" * 60
    )
    print(
        "Fundamental Pipeline Summary"
    )
    print(
        "=" * 60
    )

    print(
        f"Total stocks: {len(symbols)}"
    )

    print(
        f"Successful stocks: {success_count}"
    )

    print(
        f"Partial stocks: {partial_count}"
    )

    print(
        f"No data stocks: {no_data_count}"
    )

    print(
        f"Total processed records: "
        f"{total_processed}"
    )

    if no_data_symbols:

        print(
            "No data stocks: "
            f"{', '.join(no_data_symbols)}"
        )

    if failed_symbols:

        print(
            "Failed stocks: "
            f"{', '.join(failed_symbols)}"
        )

    else:

        print(
            "Failed stocks: 0"
        )

    print(
        "Fundamental data ingestion "
        "completed."
    )

    return total_processed
