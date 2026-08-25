from datetime import date
from time import time

import requests


class TWSECalendarProvider:
    """
    Provider for Taiwan Stock Exchange (TWSE)
    official market holiday calendar.
    """

    BASE_URL = (
        "https://www.twse.com.tw/"
        "rwd/zh/holidaySchedule/holidaySchedule"
    )

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch_calendar(self) -> dict:
        """
        Fetch the current TWSE market calendar.

        Returns
        -------
        dict
            Raw TWSE calendar response.
        """

        params = {
            "response": "json",
            "_": str(int(time() * 1000)),
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise RuntimeError(
                "TWSE calendar response must be a mapping"
            )

        return payload

    def get_closed_dates(self) -> set[date]:
        """
        Return TWSE closed-market dates.

        TWSE's annual calendar contains both:
        - trading days
        - non-trading days

        Only rows that do not indicate a trading day
        are treated as closed-market dates.
        """

        payload = self.fetch_calendar()

        fields = payload.get(
            "fields",
            [],
        )

        data = payload.get(
            "data",
            [],
        )

        if not fields:
            raise RuntimeError(
                "TWSE calendar response has no fields"
            )

        if not data:
            raise RuntimeError(
                "TWSE calendar response has no data"
            )

        try:
            date_index = fields.index("日期")
            name_index = fields.index("名稱")
        except ValueError as exc:
            raise RuntimeError(
                "TWSE calendar response is missing "
                "required fields"
            ) from exc

        closed_dates = set()

        for row in data:

            if len(row) <= max(
                date_index,
                name_index,
            ):
                continue

            raw_date = row[date_index]
            name = str(row[name_index])

            if "交易日" in name:
                continue

            try:
                closed_date = date.fromisoformat(
                    raw_date
                )
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid TWSE calendar date: "
                    f"{raw_date}"
                ) from exc

            closed_dates.add(closed_date)

        return closed_dates