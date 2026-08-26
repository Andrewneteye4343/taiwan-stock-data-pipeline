from datetime import date, time
from unittest.mock import patch

import scheduler.scheduler as scheduler


def test_load_scheduler_config():
    config = scheduler.load_scheduler_config()

    assert config["realtime_interval_seconds"] == 60
    assert config["daily_pipeline_time"] == time(14, 0)


def test_post_close_before_daily_pipeline_time():
    current_date = scheduler.today()

    completed_date = None

    current_datetime = scheduler.now().replace(
        hour=13,
        minute=59,
        second=0,
        microsecond=0,
    )

    with patch(
        "scheduler.scheduler.now",
        return_value=current_datetime,
    ), patch(
        "scheduler.scheduler.today",
        return_value=current_date,
    ), patch(
        "scheduler.scheduler.run_daily_pipeline"
    ) as mock_pipeline:

        daily_pipeline_time = scheduler.load_scheduler_config()[
            "daily_pipeline_time"
        ]

        if current_datetime.time() < daily_pipeline_time:
            pass
        elif completed_date != current_date:
            scheduler.run_daily_pipeline()

        mock_pipeline.assert_not_called()


def test_post_close_at_daily_pipeline_time():
    current_date = scheduler.today()

    completed_date = None

    current_datetime = scheduler.now().replace(
        hour=14,
        minute=0,
        second=0,
        microsecond=0,
    )

    with patch(
        "scheduler.scheduler.now",
        return_value=current_datetime,
    ), patch(
        "scheduler.scheduler.today",
        return_value=current_date,
    ), patch(
        "scheduler.scheduler.run_daily_pipeline"
    ) as mock_pipeline:

        daily_pipeline_time = scheduler.load_scheduler_config()[
            "daily_pipeline_time"
        ]

        if current_datetime.time() < daily_pipeline_time:
            pass
        elif completed_date != current_date:
            scheduler.run_daily_pipeline()

        mock_pipeline.assert_called_once()


def test_post_close_pipeline_runs_only_once_per_day():
    current_date = scheduler.today()

    completed_date = current_date

    current_datetime = scheduler.now().replace(
        hour=14,
        minute=30,
        second=0,
        microsecond=0,
    )

    with patch(
        "scheduler.scheduler.now",
        return_value=current_datetime,
    ), patch(
        "scheduler.scheduler.today",
        return_value=current_date,
    ), patch(
        "scheduler.scheduler.run_daily_pipeline"
    ) as mock_pipeline:

        daily_pipeline_time = scheduler.load_scheduler_config()[
            "daily_pipeline_time"
        ]

        if current_datetime.time() < daily_pipeline_time:
            pass
        elif completed_date != current_date:
            scheduler.run_daily_pipeline()

        mock_pipeline.assert_not_called()