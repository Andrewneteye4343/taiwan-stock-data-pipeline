import subprocess
import sys
import time
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path

import yaml

from src.core.market_session import (
    MarketSession,
    get_market_session,
)

from src.core.market_time import (
    now,
    today,
)

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "scheduler.yaml"
)


def load_scheduler_config():
    """
    Load scheduler configuration from YAML.
    """

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Scheduler config not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "Scheduler configuration must be a mapping"
        )

    if "scheduler" not in config:
        raise ValueError(
            "Missing 'scheduler' configuration"
        )

    scheduler_config = config["scheduler"]

    if not isinstance(scheduler_config, dict):
        raise ValueError(
            "'scheduler' configuration must be a mapping"
        )

    interval_seconds = scheduler_config.get(
        "realtime_interval_seconds"
    )

    daily_pipeline_time = scheduler_config.get(
        "daily_pipeline_time"
    )

    fundamental_triggers = scheduler_config.get(
        "fundamental_triggers",
        [],
    )

    retry_interval_minutes = scheduler_config.get(
        "pipeline_retry_interval_minutes",
        30,
    )

    if interval_seconds is None:
        raise ValueError(
            "Missing 'realtime_interval_seconds' "
            "configuration"
        )

    if (
        not isinstance(
            interval_seconds,
            int,
        )
        or isinstance(
            interval_seconds,
            bool,
        )
        or interval_seconds <= 0
    ):
        raise ValueError(
            "'realtime_interval_seconds' must be "
            "a positive integer"
        )

    if daily_pipeline_time is None:
        raise ValueError(
            "Missing 'daily_pipeline_time' "
            "configuration"
        )

    if not isinstance(
        daily_pipeline_time,
        str,
    ):
        raise ValueError(
            "'daily_pipeline_time' must be "
            "a string in HH:MM format"
        )

    try:

        hour, minute = (
            int(value)
            for value in daily_pipeline_time.split(":")
        )

        parsed_daily_pipeline_time = dt_time(
            hour,
            minute,
        )

    except (
        ValueError,
        TypeError,
    ):

        raise ValueError(
            "'daily_pipeline_time' must be "
            "in HH:MM format"
        )

    if not isinstance(
        fundamental_triggers,
        list,
    ):
        raise ValueError(
            "'fundamental_triggers' must be a list "
            "of '*MM-DD' strings"
        )

    if not isinstance(
        retry_interval_minutes,
        int,
    ) or retry_interval_minutes < 0:
        raise ValueError(
            "'pipeline_retry_interval_minutes' "
            "must be a non-negative integer"
        )

    return {
        "realtime_interval_seconds": interval_seconds,
        "daily_pipeline_time": parsed_daily_pipeline_time,
        "fundamental_triggers": fundamental_triggers,
        "retry_interval_minutes": retry_interval_minutes,
    }



def run_daily_pipeline():
    """
    Execute the post-close daily stock pipeline.
    """

    print(
        "========================================"
    )

    print(
        "Starting post-close daily pipeline..."
    )

    print(
        "========================================"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "update",
        ],
        check=False,
    )

    if result.returncode == 0:

        print(
            "Post-close daily pipeline completed successfully."
        )

        return True

    print(
        "Post-close daily pipeline failed."
    )

    print(
        f"Exit code: {result.returncode}"
    )

    return False


def run_quarterly_pipelines():
    """
    Execute the quarterly fundamental and dividend
    pipelines (triggered after report deadlines).
    """

    print(
        "\n========================================"
    )

    print(
        "Starting quarterly fundamental pipeline..."
    )

    print(
        "========================================"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "fundamental",
        ],
        check=False,
    )

    if result.returncode != 0:

        print(
            "Quarterly fundamental pipeline failed."
        )

        print(
            f"Exit code: {result.returncode}"
        )

    print(
        "Starting quarterly dividend pipeline..."
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "dividend",
        ],
        check=False,
    )

    if result.returncode != 0:

        print(
            "Quarterly dividend pipeline failed."
        )

        print(
            f"Exit code: {result.returncode}"
        )


def is_quarterly_trigger_active(
    current_date,
    triggers,
) -> bool:
    """
    Check whether today is on/after a quarterly trigger.

    Triggers use '*MM-DD' wildcard format,
    e.g. '*-05-15' (May 15th every year).
    """

    today_month_day = (
        f"{current_date.month:02d}-"
        f"{current_date.day:02d}"
    )

    for trigger in triggers:

        if not isinstance(trigger, str):
            continue

        if not trigger.startswith("*-"):
            continue

        trigger_month_day = trigger[2:]

        if today_month_day >= trigger_month_day:
            return True

    return False


def run_realtime_update():
    """
    Fetch realtime market data.

    Realtime data is not stored in PostgreSQL.
    """

    from src.config.stock_config import load_stocks
    from src.services.realtime_service import (
        fetch_realtime_quote,
    )

    stocks = load_stocks()

    stocks = [
        stock
        for stock in stocks
        if stock.get("enabled", True)
    ]

    print(
        "\n========================================"
    )

    print(
        "Realtime Market Update"
    )

    print(
        f"Stocks: {len(stocks)}"
    )

    print(
        "========================================"
    )

    successful = 0
    failed = 0

    for stock in stocks:

        symbol = stock["symbol"]
        name = stock["name"]

        try:

            quote = fetch_realtime_quote(
                symbol
            )

            if quote is None:

                print(
                    f"{symbol} {name}: "
                    "No realtime data"
                )

                continue

            previous_trade_price = quote.get(
                "previous_trade_price"
            )
            change = quote.get("change")
            change_pct = quote.get("change_pct")

            if change_pct is None:
                change_pct_text = "N/A"
            else:
                change_pct_text = f"{change_pct:.2f}%"

            if change is None:
                change_text = "N/A"
            else:
                change_text = str(change)

            print(
                f"{symbol} {name}: "
                f"{previous_trade_price} "
                f"({change_text}, "
                f"{change_pct_text})"
            )


            successful += 1

        except Exception as exc:

            failed += 1

            print(
                f"{symbol} {name}: "
                f"Realtime update failed - {exc}"
            )

    print(
        "----------------------------------------"
    )

    print(
        f"Realtime successful: {successful}"
    )

    print(
        f"Realtime failed: {failed}"
    )

    print(
        "Realtime data was not stored in PostgreSQL."
    )


def main():
    """
    Run the market scheduler.
    """

    config = load_scheduler_config()

    realtime_interval = config[
        "realtime_interval_seconds"
    ]

    daily_pipeline_time = config[
        "daily_pipeline_time"
    ]

    fundamental_triggers = config[
        "fundamental_triggers"
    ]

    retry_interval_minutes = config[
        "retry_interval_minutes"
    ]
    
    print(
        "========================================"
    )

    print(
        "Stock Market Scheduler"
    )

    print(
        "Realtime interval: "
        f"{realtime_interval} seconds"
    )

    print(
        "========================================"
    )

    last_session = None
    post_close_completed_date = None
    daily_failed_date = None
    quarterly_completed_date = None

    while True:
    
        session = get_market_session()

        current_date = today()

        print(
            "\n========================================"
        )

        print(
            f"Market session: {session.value}"
        )

        print(
            "========================================"
        )

        if session == MarketSession.TRADING:

            # A new trading day has started,
            # so allow post-close execution again.
            if (
                post_close_completed_date
                != current_date
            ):
                post_close_completed_date = None

            run_realtime_update()

            wait_seconds = realtime_interval

        elif session == MarketSession.POST_CLOSE:

            current_datetime = now()

            daily_due = (
                current_datetime.time()
                >= daily_pipeline_time
            )

            daily_done = (
                post_close_completed_date
                == current_date
            )

            if daily_due and not daily_done:

                # 日行情管線（含失敗重試）
                if run_daily_pipeline():

                    post_close_completed_date = (
                        current_date
                    )

                    daily_failed_date = None

                else:

                    daily_failed_date = current_date

                    print(
                        "Daily pipeline failed; "
                        "will retry after "
                        f"{retry_interval_minutes} minutes."
                    )

            elif (
                daily_due
                and daily_failed_date == current_date
            ):

                # 重試已失敗的日行情管線
                retry_at = (
                    datetime.combine(
                        current_date,
                        daily_pipeline_time,
                    )
                    + timedelta(
                        minutes=retry_interval_minutes
                    )
                )

                if current_datetime >= retry_at:

                    if run_daily_pipeline():

                        post_close_completed_date = (
                            current_date
                        )

                        daily_failed_date = None

            elif (
                daily_done
                and quarterly_completed_date
                != current_date
                and is_quarterly_trigger_active(
                    current_date,
                    fundamental_triggers,
                )
            ):

                # 季報/股利管線（每季財報期限後執行一次）
                run_quarterly_pipelines()

                quarterly_completed_date = (
                    current_date
                )

            else:

                print(
                    "Post-close pipeline already "
                    "completed for today."
                )

            wait_seconds = realtime_interval

        else:

            print(
                "Market is currently closed."
            )

            wait_seconds = realtime_interval

        print(
            f"\nWaiting {wait_seconds} seconds..."
        )

        time.sleep(
            wait_seconds
        )


if __name__ == "__main__":
    main()