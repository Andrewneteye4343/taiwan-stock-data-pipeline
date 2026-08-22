import argparse

from src.api.twse import fetch_twse_api
from src.collector.fundamental_data import (
    normalize_twse_financial_data,
    normalize_twse_balance_sheet_data,
    merge_twse_financial_and_balance_sheet,
    parse_financial_data,
)
from src.etl.load import load_fundamental_data


TWSE_FUNDAMENTAL_ENDPOINT = "opendata/t187ap06_L_ci"
TWSE_BALANCE_SHEET_ENDPOINT = "opendata/t187ap07_L_ci"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect TWSE fundamental data."
    )

    parser.add_argument(
        "--symbol",
        help="Stock symbol to collect, e.g. 2330",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    # =========================================================
    # 1. Fetch income statement data
    # =========================================================

    print("Fetching TWSE financial data...")

    financial_raw_data = fetch_twse_api(
        TWSE_FUNDAMENTAL_ENDPOINT
    )

    print(
        f"Total TWSE financial records: "
        f"{len(financial_raw_data)}"
    )

    # =========================================================
    # 2. Fetch balance sheet data
    # =========================================================

    print("Fetching TWSE balance sheet data...")

    balance_raw_data = fetch_twse_api(
        TWSE_BALANCE_SHEET_ENDPOINT
    )

    print(
        f"Total TWSE balance sheet records: "
        f"{len(balance_raw_data)}"
    )

    # =========================================================
    # 3. Filter by symbol
    # =========================================================

    if args.symbol:

        financial_raw_data = [
            row
            for row in financial_raw_data
            if row.get("公司代號") == args.symbol
        ]

        balance_raw_data = [
            row
            for row in balance_raw_data
            if row.get("公司代號") == args.symbol
        ]

        print(
            f"Filtered financial records for "
            f"{args.symbol}: "
            f"{len(financial_raw_data)}"
        )

        print(
            f"Filtered balance sheet records for "
            f"{args.symbol}: "
            f"{len(balance_raw_data)}"
        )

    # =========================================================
    # 4. Normalize financial data
    # =========================================================

    financial_data = normalize_twse_financial_data(
        financial_raw_data
    )

    # =========================================================
    # 5. Normalize balance sheet data
    # =========================================================

    balance_sheet_data = normalize_twse_balance_sheet_data(
        balance_raw_data
    )

    # =========================================================
    # 6. Merge financial + balance sheet data
    # =========================================================

    merged_data = merge_twse_financial_and_balance_sheet(
        financial_data,
        balance_sheet_data,
    )

    # =========================================================
    # 7. Parse into DataFrame
    # =========================================================

    fundamental_df = parse_financial_data(
        merged_data
    )

    print(
        f"Parsed fundamental records: "
        f"{len(fundamental_df)}"
    )

    # =========================================================
    # 8. Load into PostgreSQL
    # =========================================================

    processed_count = load_fundamental_data(
        fundamental_df
    )

    print(
        f"Fundamental data ingestion completed. "
        f"Processed: {processed_count}"
    )


if __name__ == "__main__":
    main()