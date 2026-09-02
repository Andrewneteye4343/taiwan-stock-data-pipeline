"""日行情資料管線（由 scripts/run_pipeline.py 遷移而來）。

統一 CLI 入口：python -m src.cli update
"""

from src.collector.market_data import MarketDataClient
from src.collector.market_pipeline import collect_stock_data
from src.config.stock_config import load_stocks
from src.core.market_time import now as market_now
from src.core.market_time import today as market_today
from src.etl.market_transform import prepare_market_data
from src.etl.pipeline import run_daily_pipeline
from src.monitoring.pipeline_logger import (
    complete_pipeline_log,
    start_pipeline_log,
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

    timestamp = market_now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print(
        f"[{timestamp}] TWSE Market Data Pipeline Summary"
    )

    print(
        f"  Total stocks: {len(stocks)}"
    )

    print(
        f"  Successful stocks: "
        f"{len(successful_symbols)}"
    )

    if no_data_symbols:

        print(
            "  No new data stocks: "
            f"{', '.join(no_data_symbols)}"
        )

    else:

        print(
            "  No new data stocks: 0"
        )

    if failed_symbols:

        print(
            "  Failed stocks: "
            f"{', '.join(failed_symbols)}"
        )

    else:

        print(
            "  Failed stocks: 0"
        )

    print(
        f"  Collected records: "
        f"{collected_count}"
    )

    print(
        f"  Processed records: "
        f"{processed_count}"
    )

    print(
        "Pipeline execution completed."
    )

    print()


def run(
    db_engine=None,
) -> int:
    """
    Execute the daily market data pipeline.

    Returns
    -------
    int
        Number of processed daily price records.
    """

    trade_date = market_today()

    log_id = start_pipeline_log(
        pipeline_name=PIPELINE_NAME,
        db_engine=db_engine,
    )

    processed_count = 0

    try:

        stocks = load_stocks()

        stocks = [
            stock
            for stock in stocks
            if stock.get("enabled", True)
        ]

        print(
            f"[{market_now().strftime('%Y-%m-%d %H:%M:%S')}] "
            "TWSE Market Data Collection"
        )
        print(
            f"  Trade date: {trade_date}"
        )
        print(
            f"  Configured stocks: {len(stocks)}"
        )

        client = MarketDataClient(
            timeout=30,
        )

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

                successful_symbols.append(symbol)

            elif status == "no_new_data":

                no_data_symbols.append(symbol)

            elif status == "failed":

                failed_symbols.append(symbol)

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

            return 0

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

        processed_count = run_daily_pipeline(
            df,
            db_engine=db_engine,
        )

        print_summary(
            stocks=stocks,
            successful_symbols=successful_symbols,
            no_data_symbols=no_data_symbols,
            failed_symbols=failed_symbols,
            collected_count=collected_count,
            processed_count=processed_count,
        )

        complete_pipeline_log(
            log_id=log_id,
            status="SUCCESS",
            records_processed=processed_count,
            db_engine=db_engine,
        )

        return processed_count

    except Exception as exc:

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

        print(
            "\nPipeline execution failed:"
        )

        print(
            error_message
        )

        raise


def main(
    db_engine=None,
) -> int:
    """
    Compatibility entry point (used by tests and
    the thin scripts/run_pipeline.py wrapper).
    """

    return run(db_engine=db_engine)
