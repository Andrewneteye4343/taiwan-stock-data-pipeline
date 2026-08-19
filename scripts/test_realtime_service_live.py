from pprint import pprint

from src.services.realtime_service import (
    fetch_realtime_quote,
)


def main():
    symbol = "2330"

    print("=" * 60)
    print(f"Fetching realtime quote: {symbol}")
    print("=" * 60)

    quote = fetch_realtime_quote(symbol)

    print("\nNormalized realtime quote:")
    pprint(quote)

    print("\nKey values:")

    fields = [
        "symbol",
        "name",
        "last_price",
        "previous_close",
        "open",
        "high",
        "low",
        "volume",
        "trade_time",
        "change",
        "change_pct",
    ]

    for field in fields:
        print(f"{field:16}: {quote.get(field)}")


if __name__ == "__main__":
    main()
