from datetime import date

import pandas as pd

from src.collector.market_data import (
    MarketDataClient,
    save_raw_data,
)

from src.collector.date_range import (
    get_date_range,
)

from src.config.stock_config import (
    load_stocks,
)

from src.etl.pipeline import (
    run_daily_pipeline,
)

from src.database.query import (
    get_latest_trade_date,
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

    print("========================================")
    print("TWSE Market Data Collection")
    print(f"Trade date: {today}")
    print(f"Configured stocks: {len(stocks)}")
    print("========================================")

    # ----------------------------------------
    # Initialize API client
    # ----------------------------------------

    client = MarketDataClient(
        timeout=30,
    )

    all_data = []

    # ----------------------------------------
    # Extract
    # ----------------------------------------

    for stock in stocks:
    
        symbol = stock["symbol"]
        name = stock["name"]

        print(
            f"\nProcessing "
            f"{symbol} {name} ..."
        )

        try:

            # ----------------------------------------
            # Get latest stored date
            # ----------------------------------------

            latest_date = get_latest_trade_date(
                symbol
            )

            if latest_date is None:

                print(
                    f"No historical data found "
                    f"for {symbol}."
                )

                dates_to_check = [
                    today
                ]

            else:

                dates_to_check = get_date_range(
                    latest_date,
                    today,
                )

            print(
                f"Latest stored date: "
                f"{latest_date}"
            )

            print(
                f"Dates to check: "
                f"{dates_to_check}"
            )


            # ----------------------------------------
            # Collect missing dates
            # ----------------------------------------

            for trade_date in dates_to_check:

                print(
                    f"  Checking "
                    f"{symbol} "
                    f"{trade_date} ..."
                )

                result = client.get_daily_data(
                    symbol=symbol,
                    trade_date=trade_date,
                )

                # Save original API response
                save_raw_data(
                    data=result,
                    symbol=symbol,
                    trade_date=trade_date,
                )

                records = result.get(
                    "data",
                    [],
                )

                if not records:

                    print(
                        f"  No trading data for "
                        f"{trade_date}."
                    )

                    continue

                all_data.extend(records)

                print(
                    f"  Collected "
                    f"{len(records)} record(s)."
                )

        except Exception as exc:

            print(
                f"Failed to collect "
                f"{symbol}: {exc}"
            )

    # ----------------------------------------
    # No data
    # ----------------------------------------

    if not all_data:

        print(
            "\nNo market data collected."
        )

        return

    # ----------------------------------------
    # DataFrame
    # ----------------------------------------
    stock_metadata = pd.DataFrame(stocks)

    df = pd.DataFrame(
        all_data
    )

    df = df.merge(
        stock_metadata[
            [
                "symbol",
                "market",
                "industry",
            ]
        ],
        on="symbol",
        how="left",
        )

    print("\nCollected Data:")

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

    processed_count = run_daily_pipeline(df)

    print(
        "\n========================================"
    )

    print(
        "Pipeline execution completed."
    )

    print(
        f"Processed: "
        f"{processed_count} records"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()