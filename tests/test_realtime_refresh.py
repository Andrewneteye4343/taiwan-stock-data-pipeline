from dashboard.components.realtime import (
    normalize_refresh_interval,
)


def test_normalize_refresh_interval_default():
    assert normalize_refresh_interval(None) == 60


def test_normalize_refresh_interval_30_seconds():
    assert normalize_refresh_interval(30) == 30


def test_normalize_refresh_interval_60_seconds():
    assert normalize_refresh_interval(60) == 60


def test_normalize_refresh_interval_300_seconds():
    assert normalize_refresh_interval(300) == 300


def test_normalize_refresh_interval_invalid_value():
    assert normalize_refresh_interval(5) == 60


def test_normalize_refresh_interval_zero():
    assert normalize_refresh_interval(0) == 60

def test_get_refresh_options():
    from dashboard.components.realtime import (
        get_refresh_options,
    )

    options = get_refresh_options()

    assert options == {
        "30 秒": 30,
        "60 秒": 60,
        "5 分鐘": 300,
    }