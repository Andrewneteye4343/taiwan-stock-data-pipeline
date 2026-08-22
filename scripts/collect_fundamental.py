import argparse
from pathlib import Path

import yaml

from src.api.twse import fetch_twse_api
from src.collector.fundamental_data import (
    normalize_twse_balance_sheet_data,
    normalize_twse_financial_data,
    merge_twse_financial_and_balance_sheet,
    parse_financial_data,
)
from src.etl.load import load_fundamental_data


# ============================================================
# Configuration
# ============================================================

TWSE_FUNDAMENTAL_ENDPOINT = (
    "opendata/t187ap06_L_ci"
)

TWSE_BALANCE_SHEET_ENDPOINT = (
    "opendata/t187ap07_L_ci"
)

STOCK_CONFIG_PATH = Path(
    "config/stocks.yaml"
)


# ============================================================
# Argument Parser
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Collect TWSE fundamental data "
            "for enabled stocks."
        )
    )

    parser.add_argument(
        "--symbol",
        help=(
            "Stock symbol to collect. "
            "If omitted, all enabled stocks "
            "with type=stock in stocks.yaml "
            "are processed."
        ),
    )

    return parser.parse_args()


# ============================================================
# Stock Configuration
# ============================================================

def load_stock_config():
    """
    Load stock configuration from stocks.yaml.

    Expected structure:

    stocks:
      - symbol: "2330"
        name: "台積電"
        type: "stock"
        enabled: true
    """

    if not STOCK_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Stock config not found: "
            f"{STOCK_CONFIG_PATH}"
        )

    with STOCK_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    if not config:
        raise ValueError(
            "stocks.yaml is empty."
        )

    stocks = config.get("stocks")

    if not isinstance(stocks, list):
        raise ValueError(
            "stocks.yaml must contain "
            "a 'stocks' list."
        )

    return stocks


def get_enabled_stock_symbols():
    """
    Return enabled symbols whose type is 'stock'.

    Only instruments satisfying both conditions
    are included:

    - enabled: true
    - type: stock

    This prevents ETFs and other instrument types
    from entering the stock fundamental pipeline.
    """

    stocks = load_stock_config()

    enabled_stock_symbols = []

    for stock in stocks:

        if not isinstance(stock, dict):
            continue

        symbol = stock.get("symbol")

        instrument_type = stock.get(
            "type"
        )

        enabled = stock.get(
            "enabled",
            False,
        )

        if not symbol:
            continue

        if enabled is not True:
            continue

        if instrument_type != "stock":
            continue

        enabled_stock_symbols.append(
            str(symbol)
        )

    return enabled_stock_symbols


def get_stock_config(symbol):
    """
    Return configuration for a specific symbol.

    Returns
    -------
    dict | None
        Matching stock configuration.
    """

    stocks = load_stock_config()

    for stock in stocks:

        if not isinstance(stock, dict):
            continue

        if str(stock.get("symbol")) == str(symbol):
            return stock

    return None


# ============================================================
# TWSE Data Collection
# ============================================================

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


# ============================================================
# Process One Stock
# ============================================================

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
        - "success"
        - "partial"
        - "no_data"

    SUCCESS
        Both financial and balance sheet data exist.

    PARTIAL
        Only one of financial or balance sheet
        data exists.

    NO_DATA
        Neither financial nor balance sheet
        data exists.

    Exceptions are intentionally not caught here.
    They are handled by main() and classified
    as FAILED.
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

    # --------------------------------------------------------
    # Filter financial data
    # --------------------------------------------------------

    financial_data = [
        row
        for row in financial_raw
        if str(row.get("公司代號")) == str(symbol)
    ]

    # --------------------------------------------------------
    # Filter balance sheet data
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Determine data availability
    # --------------------------------------------------------

    has_financial = bool(
        financial_data
    )

    has_balance = bool(
        balance_data
    )

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if not has_financial and not has_balance:

        print(
            f"[WARNING] No financial data "
            f"found for {symbol}"
        )

        print(
            f"[WARNING] No balance sheet data "
            f"found for {symbol}"
        )

        print(
            f"[WARNING] No fundamental data "
            f"available for {symbol}"
        )

        return 0, "no_data"

    # --------------------------------------------------------
    # PARTIAL DATA
    # --------------------------------------------------------

    if not has_financial:

        print(
            f"[WARNING] No financial data "
            f"found for {symbol}"
        )

        print(
            f"[WARNING] Partial fundamental data "
            f"for {symbol}: "
            "balance sheet data is available."
        )

    elif not has_balance:

        print(
            f"[WARNING] No balance sheet data "
            f"found for {symbol}"
        )

        print(
            f"[WARNING] Partial fundamental data "
            f"for {symbol}: "
            "financial data is available."
        )

    # --------------------------------------------------------
    # Normalize financial data
    # --------------------------------------------------------

    normalized_financial = (
        normalize_twse_financial_data(
            financial_data
        )
        if has_financial
        else []
    )

    # --------------------------------------------------------
    # Normalize balance sheet data
    # --------------------------------------------------------

    normalized_balance = (
        normalize_twse_balance_sheet_data(
            balance_data
        )
        if has_balance
        else []
    )

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    merged_data = (
        merge_twse_financial_and_balance_sheet(
            normalized_financial,
            normalized_balance,
        )
    )

    # --------------------------------------------------------
    # Parse
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    processed_count = (
        load_fundamental_data(
            fundamental_df
        )
    )

    print(
        f"Successfully processed "
        f"{processed_count} fundamental "
        f"records for {symbol}."
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    if has_financial and has_balance:

        return processed_count, "success"

    return processed_count, "partial"


# ============================================================
# Main Pipeline
# ============================================================

def main():

    args = parse_args()

    print(
        "Starting TWSE Fundamental Pipeline..."
    )

    # --------------------------------------------------------
    # Determine symbols
    # --------------------------------------------------------

    if args.symbol:

        symbol = str(
            args.symbol
        )

        stock_config = get_stock_config(
            symbol
        )

        if stock_config is None:

            raise ValueError(
                f"Symbol {symbol} "
                "is not configured in stocks.yaml."
            )

        instrument_type = stock_config.get(
            "type"
        )

        enabled = stock_config.get(
            "enabled",
            False,
        )

        print(
            "Mode: single stock"
        )

        print(
            f"Symbol: {symbol}"
        )

        print(
            f"Type: {instrument_type}"
        )

        print(
            f"Enabled: {enabled}"
        )

        # ----------------------------------------------------
        # Validate instrument type
        # ----------------------------------------------------

        if instrument_type != "stock":

            print(
                f"[WARNING] {symbol} has "
                f"type='{instrument_type}'."
            )

            print(
                "Fundamental Pipeline only "
                "processes type='stock'."
            )

            print(
                "Skipping symbol."
            )

            return

        symbols = [
            symbol
        ]

    else:

        symbols = (
            get_enabled_stock_symbols()
        )

        print(
            "Mode: enabled stocks from "
            "stocks.yaml"
        )

    # --------------------------------------------------------
    # Validate symbols
    # --------------------------------------------------------

    if not symbols:

        print(
            "No enabled stocks to process."
        )

        return

    print(
        "Stocks to process: "
        f"{', '.join(symbols)}"
    )

    # --------------------------------------------------------
    # Fetch TWSE data once
    # --------------------------------------------------------

    financial_raw, balance_raw = (
        fetch_fundamental_data()
    )

    # --------------------------------------------------------
    # Process stocks
    # --------------------------------------------------------

    total_processed = 0

    success_count = 0

    partial_count = 0

    no_data_count = 0

    no_data_symbols = []

    failed_symbols = []

    for symbol in symbols:

        try:

            processed_count, status = (
                process_symbol(
                    symbol,
                    financial_raw,
                    balance_raw,
                )
            )

            total_processed += (
                processed_count
            )

            if status == "success":

                success_count += 1

            elif status == "partial":

                partial_count += 1

            elif status == "no_data":

                no_data_count += 1

                no_data_symbols.append(
                    symbol
                )

        except Exception as exc:

            print()
            print(
                f"[ERROR] Failed to process "
                f"{symbol}: {exc}"
            )

            failed_symbols.append(
                symbol
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

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
        f"Total stocks: "
        f"{len(symbols)}"
    )

    print(
        f"Successful stocks: "
        f"{success_count}"
    )

    print(
        f"Partial stocks: "
        f"{partial_count}"
    )

    print(
        f"No data stocks: "
        f"{no_data_count}"
    )

    print(
        f"Total processed records: "
        f"{total_processed}"
    )

    # --------------------------------------------------------
    # No data stocks
    # --------------------------------------------------------

    if no_data_symbols:

        print(
            "No data stocks: "
            f"{', '.join(no_data_symbols)}"
        )

    # --------------------------------------------------------
    # Failed stocks
    # --------------------------------------------------------

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


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()