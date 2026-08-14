import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


def main():
    print("Loading stock prices into DataFrame...")
    print()

    sql = text("""
        SELECT
            s.symbol,
            s.name,
            d.trade_date,
            d.open,
            d.high,
            d.low,
            d.close,
            d.volume,
            d.turnover
        FROM stock_master AS s
        JOIN daily_price AS d
            ON s.stock_id = d.stock_id
        ORDER BY
            s.symbol,
            d.trade_date DESC;
    """)

    try:
        with engine.connect() as connection:
            df = pd.read_sql(sql, connection)

        print("DataFrame:")
        print(df)

        print()
        print("-" * 70)
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print()
        print("Data Types:")
        print(df.dtypes)

    except Exception as e:
        print("Failed to load DataFrame!")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()