import pandas as pd
from sqlalchemy import text

from src.database.connection import engine
from src.etl.transform import transform_daily_price
from src.etl.validate import validate_daily_price
from src.etl.load import load_daily_price


def main():

    print("Loading source data...")
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

    # Transform
    df = transform_daily_price(df)

    # Validate
    validate_daily_price(df)

    # Load
    load_daily_price(df)

    print()
    print("Extract + Transform + Validate + Load completed.")


if __name__ == "__main__":
    main()