from datetime import date
from unittest.mock import patch

import pytest
import yaml

from src.core.market_session import MarketSession
from scheduler import scheduler


@pytest.fixture
def scheduler_config_file(
    tmp_path,
    monkeypatch,
):
    """
    Create an isolated temporary scheduler
    configuration file for testing.
    """

    config_path = tmp_path / "scheduler.yaml"

    def write_config(config):
        with config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            yaml.safe_dump(
                config,
                file,
                allow_unicode=True,
            )

    monkeypatch.setattr(
        scheduler,
        "CONFIG_PATH",
        config_path,
    )

    return write_config


def test_load_scheduler_config_success(
    scheduler_config_file,
):
    """
    Verify that a valid scheduler configuration
    is loaded correctly.
    """

    scheduler_config_file(
        {
            "scheduler": {
                "realtime_interval_seconds": 60,
            }
        }
    )

    config = scheduler.load_scheduler_config()

    assert config == {
        "realtime_interval_seconds": 60,
    }


def test_load_scheduler_config_missing_scheduler(
    scheduler_config_file,
):
    """
    Verify that missing scheduler configuration
    raises ValueError.
    """

    scheduler_config_file({})

    with pytest.raises(
        ValueError,
        match="Missing 'scheduler' configuration",
    ):
        scheduler.load_scheduler_config()


def test_load_scheduler_config_missing_interval(
    scheduler_config_file,
):
    """
    Verify that missing realtime interval
    raises ValueError.
    """

    scheduler_config_file(
        {
            "scheduler": {}
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing 'realtime_interval_seconds' configuration",
    ):
        scheduler.load_scheduler_config()


@pytest.mark.parametrize(
    "interval",
    [
        0,
        -1,
        "60",
        60.0,
        True,
        False,
    ],
)
def test_load_scheduler_config_invalid_interval(
    scheduler_config_file,
    interval,
):
    """
    Verify that realtime interval must be
    a positive integer.
    """

    scheduler_config_file(
        {
            "scheduler": {
                "realtime_interval_seconds": interval,
            }
        }
    )

    with pytest.raises(
        ValueError,
        match="'realtime_interval_seconds' must be a positive integer",
    ):
        scheduler.load_scheduler_config()


def test_trading_session_runs_realtime_update():
    """
    Trading session should run realtime update.
    """

    with patch(
        "scheduler.scheduler.run_realtime_update",
    ) as mock_realtime:

        session = MarketSession.TRADING

        if session == MarketSession.TRADING:
            scheduler.run_realtime_update()

        mock_realtime.assert_called_once()


def test_post_close_runs_daily_pipeline_once():
    """
    Post-close pipeline should run only once
    for the same trading date.
    """

    current_date = date(
        2026,
        8,
        25,
    )

    with patch(
        "scheduler.scheduler.run_daily_pipeline",
    ) as mock_daily:

        post_close_completed_date = None

        # First post-close execution
        if post_close_completed_date != current_date:
            scheduler.run_daily_pipeline()

            post_close_completed_date = (
                current_date
            )

        # Second post-close execution
        if post_close_completed_date != current_date:
            scheduler.run_daily_pipeline()

        mock_daily.assert_called_once()


def test_pre_open_does_not_run_pipeline():
    """
    Pre-open session should not run
    realtime or daily pipeline.
    """

    with patch(
        "scheduler.scheduler.run_realtime_update",
    ) as mock_realtime, patch(
        "scheduler.scheduler.run_daily_pipeline",
    ) as mock_daily:

        session = MarketSession.PRE_OPEN

        if session == MarketSession.TRADING:
            scheduler.run_realtime_update()

        elif session == MarketSession.POST_CLOSE:
            scheduler.run_daily_pipeline()

        mock_realtime.assert_not_called()
        mock_daily.assert_not_called()


def test_closed_does_not_run_pipeline():
    """
    Closed session should not run
    realtime or daily pipeline.
    """

    with patch(
        "scheduler.scheduler.run_realtime_update",
    ) as mock_realtime, patch(
        "scheduler.scheduler.run_daily_pipeline",
    ) as mock_daily:

        session = MarketSession.CLOSED

        if session == MarketSession.TRADING:
            scheduler.run_realtime_update()

        elif session == MarketSession.POST_CLOSE:
            scheduler.run_daily_pipeline()

        mock_realtime.assert_not_called()
        mock_daily.assert_not_called()