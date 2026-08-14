from sqlalchemy import text

from src.database.connection import engine


def main():
    sql = text("""
        SELECT
            conname,
            contype,
            pg_get_constraintdef(oid) AS definition
        FROM pg_constraint
        WHERE conrelid = 'daily_price'::regclass
        ORDER BY conname;
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        print("daily_price constraints:")
        print("-" * 80)

        for row in result:
            print(
                f"{row.conname} | "
                f"{row.contype} | "
                f"{row.definition}"
            )

        print("-" * 80)


if __name__ == "__main__":
    main()