from sqlalchemy import text

from src.database.connection import engine


def main():
    print("Querying stock_master...")
    print()

    sql = text("""
        SELECT
            stock_id,
            symbol,
            name,
            market,
            industry,
            listed_date
        FROM stock_master
        ORDER BY symbol;
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(sql)

            rows = result.fetchall()

            print("Stock Master:")
            print("-" * 70)

            for row in rows:
                print(
                    f"{row.stock_id} | "
                    f"{row.symbol} | "
                    f"{row.name} | "
                    f"{row.market} | "
                    f"{row.industry} | "
                    f"{row.listed_date}"
                )

            print("-" * 70)
            print(f"Total stocks: {len(rows)}")

    except Exception as e:
        print("Failed to query stock_master!")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()