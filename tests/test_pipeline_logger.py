from sqlalchemy import text

from src.monitoring.pipeline_logger import (
    start_pipeline_log,
    complete_pipeline_log,
)


def test_pipeline_logger(test_engine):
    """
    Test pipeline log creation and completion.

    The test must use the test database engine
    provided by the test_engine fixture.
    """

    pipeline_name = "test_pipeline"

    log_id = start_pipeline_log(
        pipeline_name=pipeline_name,
        db_engine=test_engine,
    )

    assert isinstance(
        log_id,
        int,
    )

    complete_pipeline_log(
        log_id=log_id,
        status="SUCCESS",
        records_processed=3,
        db_engine=test_engine,
    )

    with test_engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    pipeline_name,
                    status,
                    records_processed,
                    error_message
                FROM pipeline_log
                WHERE log_id = :log_id;
                """
            ),
            {
                "log_id": log_id,
            },
        )

        row = result.fetchone()

    assert row is not None

    assert row.pipeline_name == pipeline_name

    assert row.status == "SUCCESS"

    assert row.records_processed == 3

    assert row.error_message is None

    # ----------------------------------------
    # Cleanup test record
    # ----------------------------------------

    with test_engine.begin() as connection:

        connection.execute(
            text(
                """
                DELETE FROM pipeline_log
                WHERE log_id = :log_id;
                """
            ),
            {
                "log_id": log_id,
            },
        )