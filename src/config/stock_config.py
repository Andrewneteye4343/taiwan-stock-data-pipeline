from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

STOCK_CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "stocks.yaml"
)


def load_stocks() -> list[dict]:
    """
    Load stock configuration from stocks.yaml.
    """

    if not STOCK_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Stock configuration not found: "
            f"{STOCK_CONFIG_PATH}"
        )

    with open(
        STOCK_CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        config = yaml.safe_load(file)

    if not config:
        raise ValueError(
            "Stock configuration is empty."
        )

    stocks = config.get("stocks")

    if not stocks:
        raise ValueError(
            "No stocks found in stocks.yaml."
        )

    return stocks