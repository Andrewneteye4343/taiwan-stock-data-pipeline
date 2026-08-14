from sqlalchemy import text

from src.database.connection import engine


def main():
    print("Connecting to PostgreSQL...")

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

            print("PostgreSQL connection successful!")
            print(f"Database test result: {value}")

    except Exception as e:
        print("PostgreSQL connection failed!")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()