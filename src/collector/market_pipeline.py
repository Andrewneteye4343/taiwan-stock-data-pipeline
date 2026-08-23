from src.collector.date_range import get_date_range
from src.collector.market_data import save_raw_data
from src.database.query import get_latest_trade_date

def collect_stock_data(
    stock,
    client,
    today,
):
    """
    Collect missing market data for one stock.

    Returns
    -------
    tuple[list[dict], str]
        records, status

    status:
        - "success"
        - "no_new_data"
        - "failed"
    """

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

        collected_records = []

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

            collected_records.extend(
                records
            )

            print(
                f"  Collected "
                f"{len(records)} record(s)."
            )

        # ----------------------------------------
        # Determine status
        # ----------------------------------------

        if not collected_records:

            return [], "no_new_data"

        return (
            collected_records,
            "success",
        )

    except Exception as exc:

        print(
            f"Failed to collect "
            f"{symbol}: {exc}"
        )

        return [], "failed"