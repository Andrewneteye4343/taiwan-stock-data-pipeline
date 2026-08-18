import pandas as pd


def _parse_numeric(value):
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


def parse_financial_data(
    raw_data: list[dict],
) -> pd.DataFrame:
    """
    Parse raw fundamental financial data.

    Expected required fields:
    - symbol
    - report_year
    - report_quarter

    Optional financial fields:
    - eps
    - eps_ytd
    - bvps
    - dps

    Returns
    -------
    pd.DataFrame
        Standardized financial data with columns:
        symbol
        report_year
        report_quarter
        eps
        eps_ytd
        bvps
        dps
    """

    records = []

    for item in raw_data:
        records.append(
            {
                "symbol": str(item["symbol"]),
                "report_year": int(item["report_year"]),
                "report_quarter": int(item["report_quarter"]),
                "eps": _parse_numeric(item.get("eps")),
                "eps_ytd": _parse_numeric(item.get("eps_ytd")),
                "bvps": _parse_numeric(item.get("bvps")),
                "dps": _parse_numeric(item.get("dps")),
            }
        )

    result = pd.DataFrame(
        records,
        columns=[
            "symbol",
            "report_year",
            "report_quarter",
            "eps",
            "eps_ytd",
            "bvps",
            "dps",
        ],
    )

    result = (
        result.sort_values(
            by=[
                "symbol",
                "report_year",
                "report_quarter",
            ]
        )
        .drop_duplicates(
            subset=[
                "symbol",
                "report_year",
                "report_quarter",
            ],
            keep="last",
        )
        .reset_index(drop=True)
    )

    return result