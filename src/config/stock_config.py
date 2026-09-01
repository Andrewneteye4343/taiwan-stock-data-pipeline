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


def get_enabled_symbols(
    types: tuple[str, ...] | None = None,
) -> list[str]:
    """
    Return enabled stock symbols.

    Parameters
    ----------
    types : tuple[str, ...] | None
        Instrument types to include.
        If None, all enabled instruments are returned.
        Example: ("stock",) for stocks only.
    """

    symbols = []

    for stock in load_stocks():

        if not isinstance(stock, dict):
            continue

        if stock.get("enabled") is not True:
            continue

        if types is not None:

            if stock.get("type") not in types:
                continue

        symbol = stock.get("symbol")

        if symbol:
            symbols.append(str(symbol))

    return symbols


def get_stock_config(
    symbol: str,
) -> dict | None:
    """
    Return the configuration for a specific symbol.

    Returns
    -------
    dict | None
        Matching stock configuration, or None.
    """

    for stock in load_stocks():

        if not isinstance(stock, dict):
            continue

        if str(stock.get("symbol")) == str(symbol):
            return stock

    return None