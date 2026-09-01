"""日行情管線入口（薄包裝，邏輯已遷移至 src/pipelines/market_daily.py）。

建議改用統一 CLI：python -m src.cli update
保留此檔以相容既有 docker-compose 指令與整合測試。
"""

from src.pipelines.market_daily import PIPELINE_NAME, run


def main(db_engine=None):
    return run(db_engine=db_engine)


if __name__ == "__main__":
    main()
