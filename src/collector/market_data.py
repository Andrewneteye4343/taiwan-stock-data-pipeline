from datetime import date
from pathlib import Path
import json

import requests


class MarketDataClient:
    """
    Client for Taiwan Stock Exchange (TWSE)
    official public market data API.
    """

    BASE_URL = (
        "https://www.twse.com.tw/"
        "exchangeReport/STOCK_DAY"
    )

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get_daily_data(
        self,
        symbol: str,
        trade_date: date,
    ) -> dict:
        """
        Retrieve daily trading data for a stock.

        TWSE STOCK_DAY returns the trading data
        for the specified month.

        Parameters
        ----------
        symbol : str
            Stock symbol, e.g. "2330".

        trade_date : date
            Target trading date.

        Returns
        -------
        dict
            Normalized records containing:

            symbol
            name
            trade_date
            open
            high
            low
            close
            volume
            turnover
        """

        # TWSE API requires the first day of the month.
        month_date = trade_date.replace(day=1)

        params = {
            "response": "json",
            "date": month_date.strftime("%Y%m%d"),
            "stockNo": symbol,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("stat") != "OK":
            raise RuntimeError(
                f"TWSE API request failed: "
                f"{payload.get('stat')}"
            )

        return self._parse_response(
            payload=payload,
            symbol=symbol,
            trade_date=trade_date,
        )

    @staticmethod
    def _parse_response(
        payload: dict,
        symbol: str,
        trade_date: date,
    ) -> dict:
        """
        Convert TWSE response format into
        our internal data format.
        """

        fields = payload.get("fields", [])
        data = payload.get("data", [])

        if not data:
            return {
                "symbol": symbol,
                "name": None,
                "data": [],
            }

        # Find column indexes from TWSE field names.
        field_map = {
            field: index
            for index, field in enumerate(fields)
        }

        required_fields = [
            "日期",
            "成交股數",
            "成交金額",
            "開盤價",
            "最高價",
            "最低價",
            "收盤價",
        ]

        for field in required_fields:
            if field not in field_map:
                raise RuntimeError(
                    f"TWSE response missing field: {field}"
                )

        # Extract stock name from title if available.
        title = payload.get("title", "")

        name = None

        if symbol in title:
            parts = title.split()

            if len(parts) >= 3:
                name = parts[-2]

        records = []

        for row in data:

            raw_date = row[field_map["日期"]]

            # TWSE date format:
            # 115/08/14
            year, month, day = (
                int(x)
                for x in raw_date.split("/")
            )

            converted_date = date(
                year + 1911,
                month,
                day,
            )

            # We only want the requested trading date.
            if converted_date != trade_date:
                continue

            def parse_number(value):
                if value in ("--", "", None):
                    return None

                return float(
                    str(value).replace(",", "")
                )

            record = {
                "symbol": symbol,
                "name": name,
                "trade_date": converted_date,
                "open": parse_number(
                    row[field_map["開盤價"]]
                ),
                "high": parse_number(
                    row[field_map["最高價"]]
                ),
                "low": parse_number(
                    row[field_map["最低價"]]
                ),
                "close": parse_number(
                    row[field_map["收盤價"]]
                ),
                "volume": int(
                    str(
                        row[field_map["成交股數"]]
                    ).replace(",", "")
                ),
                "turnover": float(
                    str(
                        row[field_map["成交金額"]]
                    ).replace(",", "")
                ),
            }

            records.append(record)

        return {
            "symbol": symbol,
            "name": name,
            "data": records,
        }


def save_raw_data(
    data: dict,
    symbol: str,
    trade_date: date,
):
    """
    Save raw API response to data/raw/.
    """

    output_dir = (
        Path("data/raw")
        / trade_date.isoformat()
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / f"{symbol}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )