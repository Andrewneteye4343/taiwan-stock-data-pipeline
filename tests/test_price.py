from sqlalchemy import text

from src.database.connection import engine


def main():

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
        FROM daily_price AS d
        JOIN stock_master AS s
            ON d.stock_id = s.stock_id
        WHERE s.symbol = '2330'
          AND d.trade_date = '2026-08-15';
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        row = result.fetchone()

    if row is None:
        print("Test record not found.")
        return

    print("Test record:")
    print("-" * 80)

    print(f"Symbol:     {row.symbol}")
    print(f"Name:       {row.name}")
    print(f"Date:       {row.trade_date}")
    print(f"Open:       {row.open}")
    print(f"High:       {row.high}")
    print(f"Low:        {row.low}")
    print(f"Close:      {row.close}")
    print(f"Volume:     {row.volume}")
    print(f"Turnover:   {row.turnover}")

    print("-" * 80)


if __name__ == "__main__":
    main()