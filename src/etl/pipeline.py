import pandas as pd

from src.etl.transform import transform_daily_price
from src.etl.validate import validate_daily_price
from src.etl.load import (
    load_stock_master,
    load_daily_price,
)


def run_daily_pipeline(
    df: pd.DataFrame,
) -> int:

    print(
        "========================================"
    )

    print(
        "Starting daily stock price pipeline..."
    )

    print(
        "========================================"
    )

    # ----------------------------------------
    # Transform
    # ----------------------------------------

    print(
        "\n[1/4] Transforming data..."
    )

    df = transform_daily_price(df)

    print(
        f"Transformed records: {len(df)}"
    )

    # ----------------------------------------
    # Validate
    # ----------------------------------------

    print(
        "\n[2/4] Validating data..."
    )

    validate_daily_price(df)

    # ----------------------------------------
    # Stock Master
    # ----------------------------------------

    print(
        "\n[3/4] Synchronizing stock master..."
    )

    load_stock_master(df)

    # ----------------------------------------
    # Daily Price
    # ----------------------------------------

    print(
        "\n[4/4] Loading daily prices..."
    )

    processed_count = load_daily_price(df)

    print(
        "\n========================================"
    )

    print(
        "Daily stock price pipeline "
        "completed successfully."
    )

    print(
        f"Processed records: {processed_count}"
    )

    print(
        "========================================"
    )

    return processed_count