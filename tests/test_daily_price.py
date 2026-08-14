from sqlalchemy import text

from src.database.connection import engine


def main():
    print("Querying stock prices...")
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
            result = connection.execute(sql)

            rows = result.fetchall()

            print("Stock Daily Prices:")
            print("-" * 100)

            for row in rows:
                print(
                    f"{row.symbol} | "
                    f"{row.name} | "
                    f"{row.trade_date} | "
                    f"Open: {row.open} | "
                    f"High: {row.high} | "
                    f"Low: {row.low} | "
                    f"Close: {row.close} | "
                    f"Volume: {row.volume} | "
                    f"Turnover: {row.turnover}"
                )

            print("-" * 100)
            print(f"Total price records: {len(rows)}")

    except Exception as e:
        print("Failed to query daily_price!")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()