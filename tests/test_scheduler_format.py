import pytest

from scheduler.scheduler import (
    format_realtime_line,
    load_scheduler_config,
)


def test_format_no_alert():
    """漲跌幅低於門檻：不標註。"""

    line = format_realtime_line(
        symbol="2330",
        name="台積電",
        price=1180.0,
        change=15.0,
        change_pct=1.29,
        alert_change_pct=2.0,
    )

    assert "2330 台積電: 1180.0 (15.0, 1.29%)" in line

    assert "⚠️" not in line


def test_format_alert_above_threshold():
    """漲跌幅 ≥ 門檻：標註警示。"""

    line = format_realtime_line(
        symbol="2330",
        name="台積電",
        price=1210.0,
        change=30.0,
        change_pct=2.61,
        alert_change_pct=2.0,
    )

    assert "⚠️" in line

    assert "漲跌幅 ≥ 2.0%" in line


def test_format_alert_negative_change():
    """跌幅的絕對值 ≥ 門檻：也要標註。"""

    line = format_realtime_line(
        symbol="2317",
        name="鴻海",
        price=245.0,
        change=-10.0,
        change_pct=-3.92,
        alert_change_pct=2.0,
    )

    assert "⚠️" in line


def test_format_alert_at_boundary():
    """恰好等於門檻：要標註（>= 語意）。"""

    line = format_realtime_line(
        symbol="2330",
        name="台積電",
        price=1180.0,
        change=23.6,
        change_pct=2.0,
        alert_change_pct=2.0,
    )

    assert "⚠️" in line


def test_format_no_pct_no_alert():
    """change_pct 為 None：不標註。"""

    line = format_realtime_line(
        symbol="2330",
        name="台積電",
        price=None,
        change=None,
        change_pct=None,
        alert_change_pct=2.0,
    )

    assert "⚠️" not in line


def test_scheduler_config_alert_threshold():

    config = load_scheduler_config()

    assert config["alert_change_pct"] == 2.0


def test_scheduler_config_invalid_alert_threshold(
    monkeypatch,
    tmp_path,
):
    """alert_change_pct 非正數時應拋錯。"""

    import scheduler.scheduler as s

    config_path = tmp_path / "scheduler.yaml"

    config_path.write_text(
        "scheduler:\n"
        "  realtime_interval_seconds: 60\n"
        "  daily_pipeline_time: '14:00'\n"
        "  alert_change_pct: 0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        s,
        "CONFIG_PATH",
        config_path,
    )

    with pytest.raises(
        ValueError,
        match="alert_change_pct",
    ):
        load_scheduler_config()
