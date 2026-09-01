"""共用資料解析工具（Phase 1：消除 fundamental/dividend 的重複實作）。"""

import pandas as pd


def parse_numeric(value):
    """
    Convert a raw numeric value into float.

    Invalid values such as "-", "", None, or non-numeric
    strings are converted to None.
    """

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

        if value == "-":
            return None

        value = value.replace(",", "")

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_date(value):
    """
    Convert a raw date value into pandas Timestamp.

    Invalid or missing dates are converted to NaT.
    """

    if value is None:
        return pd.NaT

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return pd.NaT

        if value == "-":
            return pd.NaT

    return pd.to_datetime(
        value,
        errors="coerce",
    )
