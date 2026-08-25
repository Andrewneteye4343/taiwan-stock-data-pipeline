from src.core.market_time import today as market_today

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

from src.monitoring.pipeline_logger import (
    start_pipeline_log,
    complete_pipeline_log,
)


PIPELINE_NAME = "daily_stock"


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


def main(db_engine=None):

    trade_date = market_today()

    # ----------------------------------------
    # Start pipeline execution log
    # ----------------------------------------

    log_id = start_pipeline_log(
        pipeline_name=PIPELINE_NAME,
        db_engine=db_engine,
    )

    processed_count = 0

    try:

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
            f"Trade date: {trade_date}"
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
                today=trade_date,
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

            complete_pipeline_log(
                log_id=log_id,
                status="NO_DATA",
                records_processed=0,
                db_engine=db_engine,
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
            run_daily_pipeline(
                df,
                db_engine=db_engine,
            )
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

        # ----------------------------------------
        # Complete pipeline log
        # ----------------------------------------

        complete_pipeline_log(
            log_id=log_id,
            status="SUCCESS",
            records_processed=processed_count,
            db_engine=db_engine,
        )

    except Exception as exc:

        # ----------------------------------------
        # Record pipeline failure
        # ----------------------------------------

        error_message = str(exc)

        try:

            complete_pipeline_log(
                log_id=log_id,
                status="FAILED",
                records_processed=processed_count,
                error_message=error_message,
                db_engine=db_engine,
            )

        except Exception as log_exc:

            print(
                "\nFailed to update pipeline log:"
            )

            print(
                str(log_exc)
            )

        # ----------------------------------------
        # Preserve original pipeline failure
        # ----------------------------------------

        print(
            "\nPipeline execution failed:"
        )

        print(
            error_message
        )

        raise


if __name__ == "__main__":
    main()