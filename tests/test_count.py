from sqlalchemy import text

from src.database.connection import engine


def main():

    sql = text("""
        SELECT
            COUNT(*) AS total_records
        FROM daily_price;
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        row = result.fetchone()

    print(f"Total daily_price records: {row.total_records}")


if __name__ == "__main__":
    main()