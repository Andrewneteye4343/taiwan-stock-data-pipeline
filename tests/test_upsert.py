import pandas as pd

from src.etl.transform import transform_daily_price
from src.etl.validate import validate_daily_price
from src.etl.load import load_daily_price
from src.database.connection import engine


def create_test_data() -> pd.DataFrame:
    """
    Create virtual market data for testing INSERT / UPDATE.
    """

    data = [
        {
            "symbol": "2330",
            "name": "台積電",
            "trade_date": "2026-08-15",
            "open": 1120.0,
            "high": 1140.0,
            "low": 1110.0,
            "close": 1135.0,
            "volume": 29000000,
            "turnover": 33000000000.0,
        }
    ]

    return pd.DataFrame(data)


def main():

    print("Creating virtual stock market data...")
    print()

    df = create_test_data()

    print("Raw test data:")
    print(df)

    print()
    print("-" * 70)

    # Transform
    df = transform_daily_price(df)

    print("After transformation:")
    print(df)

    print()
    print("-" * 70)

    # Validate
    validate_daily_price(df)

    print()
    print("-" * 70)

    # Load
    load_daily_price(df)

    print()
    print("Upsert test completed successfully.")


if __name__ == "__main__":
    main()