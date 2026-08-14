import pandas as pd
from sqlalchemy import text

from src.database.connection import engine
from src.etl.transform import transform_daily_price
from src.etl.validate import validate_daily_price


def main():
    print("Loading data from PostgreSQL...")
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

    with engine.connect() as connection:
        df = pd.read_sql(sql, connection)

    print("Raw data:")
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
    print("ETL Extract + Transform + Validate completed successfully.")


if __name__ == "__main__":
    main()