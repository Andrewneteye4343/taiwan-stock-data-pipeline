"""統一命令列入口（Phase 2 重構）。

用法：
    python -m src.cli update                  # 日行情 ETL（TWSE）
    python -m src.cli fundamental [--symbol]  # 季報基本面資料
    python -m src.cli dividend [--symbol]     # 股利資料
    python -m src.cli realtime                # 即時報價單次觀測
    python -m src.cli scheduler               # 啟動自動排程器
"""

import argparse
import sys


def cmd_update(args) -> None:
    from src.pipelines.market_daily import run

    run()


def cmd_fundamental(args) -> None:
    from src.pipelines.fundamental import run

    run(symbol=args.symbol)


def cmd_dividend(args) -> None:
    from src.pipelines.dividend import run

    run(symbol=args.symbol, csv_path=args.csv)


def cmd_realtime(args) -> None:
    from src.services.realtime_service import fetch_realtime_quote
    from src.config.stock_config import get_enabled_symbols

    symbols = get_enabled_symbols()

    print("TWSE Realtime Quote Observation")
    print(f"Stocks: {', '.join(symbols)}")
    print()

    for symbol in symbols:

        quote = fetch_realtime_quote(symbol)

        if quote is None:

            print(f"{symbol}: no realtime data")

            continue

        print(
            f"{symbol} {quote.get('name', '')}: "
            f"{quote.get('previous_trade_price')} "
            f"({quote.get('change')}, "
            f"{quote.get('change_pct')}%)"
        )


def cmd_scheduler(args) -> None:
    sys.path.insert(0, "scheduler")

    from scheduler import main as scheduler_main

    scheduler_main()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="taiwan-stock-data-pipeline",
        description="Taiwan stock data pipeline CLI",
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    p_update = sub.add_parser(
        "update",
        help="執行日行情 ETL 管線（TWSE）",
    )
    p_update.set_defaults(func=cmd_update)

    p_fund = sub.add_parser(
        "fundamental",
        help="執行季報基本面資料管線",
    )
    p_fund.add_argument(
        "--symbol",
        help="指定股票代號；省略則處理所有啟用的股票",
    )
    p_fund.set_defaults(func=cmd_fundamental)

    p_div = sub.add_parser(
        "dividend",
        help="執行股利資料管線（CSV 匯入）",
    )
    p_div.add_argument(
        "--symbol",
        help="指定股票代號；省略則處理所有啟用的股票",
    )
    p_div.add_argument(
        "--csv",
        help="股利 CSV 檔路徑（預設 data/dividends.csv）",
    )
    p_div.set_defaults(func=cmd_dividend)

    p_rt = sub.add_parser(
        "realtime",
        help="即時報價單次觀測",
    )
    p_rt.set_defaults(func=cmd_realtime)

    p_sched = sub.add_parser(
        "scheduler",
        help="啟動自動排程器",
    )
    p_sched.set_defaults(func=cmd_scheduler)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
