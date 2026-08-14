import pandas as pd

from src.database.connection import engine
from src.etl.pipeline import run_daily_pipeline


def main():

    print("Loading source data...")

    query = """
        SELECT
            s.symbol,
            d.trade_date,
            d.open,
            d.high,
            d.low,
            d.close,
            d.volume,
            d.turnover
        FROM stock_master s
        JOIN daily_price d
            ON s.stock_id = d.stock_id
        ORDER BY
            d.trade_date DESC,
            s.symbol;
    """

    df = pd.read_sql(
        query,
        engine,
    )

    print("\nSource Data:")
    print(df)

    print("\n" + "-" * 70)

    processed_count = run_daily_pipeline(df)

    print("\n" + "-" * 70)
    print(
        f"Pipeline processed: "
        f"{processed_count} records"
    )


if __name__ == "__main__":
    main()