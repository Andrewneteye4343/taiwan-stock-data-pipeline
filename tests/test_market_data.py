from datetime import date

from src.collector.market_data import (
    MarketDataClient,
)


def main():

    client = MarketDataClient()

    print(
        "Testing TWSE API..."
    )

    result = client.get_daily_data(
        symbol="2330",
        trade_date=date.today(),
    )

    print(
        "\nAPI Result:"
    )

    print(
        result
    )

    print(
        "\n"
        "Records:"
    )

    for record in result["data"]:

        print(
            record
        )


if __name__ == "__main__":
    main()