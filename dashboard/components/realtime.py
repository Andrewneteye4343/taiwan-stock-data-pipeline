"""即時報價載入（dashboard 用）。

注意：此處刻意不使用 st.cache_data ——
st.fragment(run_every=60) 已是唯一的刷新節奏控制，
額外的快取層會在 60 秒邊界造成「回傳舊值」的競態
（dashboard 即時行情顯示落後的根因，v2.2.1 修正）。
"""

from src.services.realtime_service import (
    fetch_realtime_quote,
)


def load_realtime_quote(symbol):
    """
    Load realtime quote for a stock symbol.
    """

    return fetch_realtime_quote(
        symbol,
        max_retries=1,
        retry_delay=3.0,
    )
