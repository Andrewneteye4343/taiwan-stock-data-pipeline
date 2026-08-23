import pandas as pd
import pytest

from dashboard.app import (
    get_stock_options,
)

from src.indicators.technical import (
    calculate_price_change,
)

def test_get_stock_options():
    options = get_stock_options()

    assert isinstance(options, list)
    assert len(options) >= 3


def test_get_stock_options_contains_expected_stocks():
    options = get_stock_options()

    symbols = [item["symbol"] for item in options]

    assert "2330" in symbols
    assert "2317" in symbols
    assert "2454" in symbols


def test_get_stock_options_contains_stock_names():
    options = get_stock_options()

    stock_map = {
        item["symbol"]: item["name"]
        for item in options
    }

    assert stock_map["2330"] == "台積電"
    assert stock_map["2317"] == "鴻海"
    assert stock_map["2454"] == "聯發科"