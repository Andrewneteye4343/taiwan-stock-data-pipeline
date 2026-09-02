"""診斷即時報價：API 抓到的價格 vs dashboard 顯示（v2.2.1 除錯用）。

用法：
    docker compose exec dashboard python scripts/diagnose_realtime.py
"""

import sys

sys.path.insert(0, ".")

from src.services.realtime_service import (
    fetch_realtime_quote,
)


def main():
    for symbol in ["2330", "2317"]:
        quote = fetch_realtime_quote(symbol)

        if quote is None:
            print(f"{symbol}: 無法取得報價")
            continue

        print(
            f"{symbol} {quote['name']}: "
            f"價格={quote['previous_trade_price']} "
            f"昨收={quote['previous_close']} "
            f"時間={quote['trade_time']} "
            f"高={quote['high']} 低={quote['low']}"
        )


if __name__ == "__main__":
    main()
