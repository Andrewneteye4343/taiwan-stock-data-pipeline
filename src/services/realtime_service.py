import requests
from datetime import datetime

TWSE_REALTIME_URL = (
    "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
)

def _to_int(value):
    if value in (None, "", "-"):
        return None

    return int(value)

def _to_float(value):
    if value in (None, "", "-", "--"):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def calculate_realtime_price_change(
    last_price,
    previous_close,
):
    if previous_close in (None, 0) or last_price is None:
        return {
            "change": None,
            "change_pct": None,
        }

    change = round(
        last_price - previous_close,
        4,
    )

    change_pct = (
        change
        / previous_close
        * 100
    )

    return {
        "change": change,
        "change_pct": change_pct,
    }

def parse_realtime_quote(
    payload: dict,
):
    """
    Parse a TWSE realtime quote response.

    Returns
    -------
    dict | None
        Normalized realtime quote data.
        Returns None when msgArray is empty or missing.
    """

    msg_array = payload.get("msgArray")

    if not msg_array:
        return None

    data = msg_array[0]

    symbol = data.get("c")
    name = data.get("n")

    trade_date_raw = data.get("d")
    trade_time = data.get("t")

    if trade_date_raw:
        trade_date = datetime.strptime(
            trade_date_raw,
            "%Y%m%d",
        ).date().isoformat()
    else:
        trade_date = None

    open_price = _to_float(data.get("o"))
    high = _to_float(data.get("h"))
    low = _to_float(data.get("l"))
    previous_close = _to_float(data.get("y"))
    last_price = _to_float(data.get("z"))

    volume_raw = data.get("v")

    if volume_raw in (None, "", "-", "--"):
        volume = None
    else:
        volume = int(volume_raw)

    if last_price is None:
        change = None
        change_pct = None
    else:
        price_change = calculate_realtime_price_change(
            last_price,
            previous_close,
        )

        change = price_change["change"]
        change_pct = price_change["change_pct"]

    return {
        "symbol": symbol,
        "name": name,
        "trade_date": trade_date,
        "trade_time": trade_time,
        "last_price": last_price,
        "open": open_price,
        "high": high,
        "low": low,
        "previous_close": previous_close,
        "change": change,
        "change_pct": change_pct,
        "volume": volume,
    }

def fetch_realtime_quote(
    symbol: str,
):
    """
    Fetch realtime quote from TWSE.

    Parameters
    ----------
    symbol : str
        Taiwan stock symbol, e.g. "2330".

    Returns
    -------
    dict | None
        Normalized realtime quote.
    """
    if symbol is None:
        raise ValueError("symbol cannot be empty")
    symbol = str(symbol).strip()

    if not symbol:
        raise ValueError("symbol cannot be empty")
    params = {
        "ex_ch": f"tse_{symbol}.tw",
        "json": "1",
        "delay": "0",
        "t": "0",
    }

    response = requests.get(
        TWSE_REALTIME_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()

    return parse_realtime_quote(payload)