from datetime import datetime

from sqlalchemy import text

from src.database.connection import engine


def start_pipeline_log(
    pipeline_name: str,
    db_engine=None,
) -> int:
    """
    Create a new pipeline execution log.

    Parameters
    ----------
    pipeline_name : str
        Name of the pipeline.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.

    Returns
    -------
    int
        Generated pipeline log ID.
    """

    if db_engine is None:
        db_engine = engine

    query = text(
        """
        INSERT INTO pipeline_log (
            pipeline_name,
            start_time,
            status,
            records_processed
        )
        VALUES (
            :pipeline_name,
            :start_time,
            'RUNNING',
            0
        )
        RETURNING log_id;
        """
    )

    with db_engine.begin() as connection:

        result = connection.execute(
            query,
            {
                "pipeline_name": pipeline_name,
                "start_time": datetime.now(),
            },
        )

        row = result.fetchone()

    return row.log_id


def complete_pipeline_log(
    log_id: int,
    status: str,
    records_processed: int = 0,
    error_message: str | None = None,
    db_engine=None,
) -> None:
    """
    Complete a pipeline execution log.

    Parameters
    ----------
    log_id : int
        Pipeline log ID.

    status : str
        Final pipeline status.

    records_processed : int
        Number of processed records.

    error_message : str | None
        Error message if the pipeline failed.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.
    """

    if db_engine is None:
        db_engine = engine

    query = text(
        """
        UPDATE pipeline_log
        SET
            end_time = :end_time,
            status = :status,
            records_processed = :records_processed,
            error_message = :error_message
        WHERE log_id = :log_id;
        """
    )

    with db_engine.begin() as connection:

        connection.execute(
            query,
            {
                "log_id": log_id,
                "end_time": datetime.now(),
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
            },
        )