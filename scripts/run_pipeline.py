from datetime import date

from src.collector.market_data import (
    MarketDataClient,
)

from src.collector.market_pipeline import (
    collect_stock_data,
)

from src.config.stock_config import (
    load_stocks,
)

from src.etl.pipeline import (
    run_daily_pipeline,
)

from src.etl.market_transform import (
    prepare_market_data,
)

def print_summary(
    stocks,
    successful_symbols,
    no_data_symbols,
    failed_symbols,
    collected_count,
    processed_count,
):
    """
    Print market data pipeline summary.
    """

    print()
    print(
        "========================================"
    )
    print(
        "TWSE Market Data Pipeline Summary"
    )
    print(
        "========================================"
    )

    print(
        f"Total stocks: {len(stocks)}"
    )

    print(
        f"Successful stocks: "
        f"{len(successful_symbols)}"
    )

    if no_data_symbols:

        print(
            "No new data stocks: "
            f"{', '.join(no_data_symbols)}"
        )

    else:

        print(
            "No new data stocks: 0"
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
        f"Collected records: "
        f"{collected_count}"
    )

    print(
        f"Processed records: "
        f"{processed_count}"
    )

    print(
        "Pipeline execution completed."
    )

    print(
        "========================================"
    )


def main():

    today = date.today()

    # ----------------------------------------
    # Load stock configuration
    # ----------------------------------------

    stocks = load_stocks()

    stocks = [
        stock
        for stock in stocks
        if stock.get("enabled", True)
    ]

    print(
        "========================================"
    )
    print(
        "TWSE Market Data Collection"
    )
    print(
        f"Trade date: {today}"
    )
    print(
        f"Configured stocks: {len(stocks)}"
    )
    print(
        "========================================"
    )

    # ----------------------------------------
    # Initialize API client
    # ----------------------------------------

    client = MarketDataClient(
        timeout=30,
    )

    # ----------------------------------------
    # Collection statistics
    # ----------------------------------------

    all_data = []

    successful_symbols = []

    no_data_symbols = []

    failed_symbols = []

    # ----------------------------------------
    # Extract
    # ----------------------------------------

    for stock in stocks:

        symbol = stock["symbol"]

        records, status = collect_stock_data(
            stock=stock,
            client=client,
            today=today,
        )

        all_data.extend(records)

        if status == "success":

            successful_symbols.append(
                symbol
            )

        elif status == "no_new_data":

            no_data_symbols.append(
                symbol
            )

        elif status == "failed":

            failed_symbols.append(
                symbol
            )

    # ----------------------------------------
    # Collection result
    # ----------------------------------------

    collected_count = len(all_data)

    if not all_data:

        print(
            "\nNo market data collected."
        )

        print_summary(
            stocks=stocks,
            successful_symbols=successful_symbols,
            no_data_symbols=no_data_symbols,
            failed_symbols=failed_symbols,
            collected_count=collected_count,
            processed_count=0,
        )

        return

    # ----------------------------------------
    # Transform
    # ----------------------------------------

    df = prepare_market_data(
        records=all_data,
        stocks=stocks,
    )

    print(
        "\nCollected Data:"
    )

    print(
        df.to_string(
            index=False
        )
    )

    print(
        f"\nTotal records: {len(df)}"
    )
    

    # ----------------------------------------
    # ETL Pipeline
    # ----------------------------------------

    processed_count = (
        run_daily_pipeline(df)
    )

    # ----------------------------------------
    # Summary
    # ----------------------------------------

    print_summary(
        stocks=stocks,
        successful_symbols=successful_symbols,
        no_data_symbols=no_data_symbols,
        failed_symbols=failed_symbols,
        collected_count=collected_count,
        processed_count=processed_count,
    )


if __name__ == "__main__":
    main()