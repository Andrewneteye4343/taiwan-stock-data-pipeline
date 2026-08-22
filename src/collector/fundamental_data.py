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

    Required fields:
    - symbol
    - report_year
    - report_quarter

    Optional financial fields:
    - eps
    - eps_ytd
    - bvps
    - dps
    - revenue
    - gross_profit
    - operating_income
    - net_income

    Returns
    -------
    pd.DataFrame
        Standardized financial data.
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
                "revenue": _parse_numeric(item.get("revenue")),
                "gross_profit": _parse_numeric(
                    item.get("gross_profit")
                ),
                "operating_income": _parse_numeric(
                    item.get("operating_income")
                ),
                "net_income": _parse_numeric(
                    item.get("net_income")
                ),
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
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
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

def normalize_twse_financial_data(
    raw_data: list[dict],
) -> list[dict]:
    """
    Convert TWSE financial API records
    into the project's internal financial schema.

    TWSE source:
    opendata/t187ap06_L_ci

    Supported fields:
    - EPS
    - Revenue
    - Gross Profit
    - Operating Income
    - Net Income
    """

    normalized = []

    for item in raw_data:

        symbol = item.get("公司代號")

        if not symbol:
            continue

        year = item.get("年度")
        quarter = item.get("季別")

        if not year or not quarter:
            continue

        normalized.append(
            {
                "symbol": str(symbol),
                "report_year": int(year) + 1911,
                "report_quarter": int(quarter),

                # EPS
                "eps": item.get(
                    "基本每股盈餘（元）"
                ),

                # Currently unavailable from this endpoint
                "eps_ytd": None,

                # BVPS will be provided by
                # t187ap07_L_ci later
                "bvps": None,

                # DPS will be provided by
                # dividend data later
                "dps": None,

                # Income statement
                "revenue": item.get(
                    "營業收入"
                ),

                "gross_profit": item.get(
                    "營業毛利（毛損）淨額"
                ),

                "operating_income": item.get(
                    "營業利益（損失）"
                ),

                "net_income": item.get(
                    "本期淨利（淨損）"
                ),
            }
        )

    return normalized

def normalize_twse_balance_sheet_data(
    raw_data: list[dict],
) -> list[dict]:
    """
    Convert TWSE balance sheet API records
    into the project's internal BVPS schema.
    """

    normalized = []

    for item in raw_data:

        symbol = item.get("公司代號")

        if not symbol:
            continue

        year = item.get("年度")
        quarter = item.get("季別")

        if not year or not quarter:
            continue

        normalized.append(
            {
                "symbol": str(symbol),
                "report_year": int(year) + 1911,
                "report_quarter": int(quarter),
                "bvps": item.get("每股參考淨值"),
            }
        )

    return normalized

def merge_twse_financial_and_balance_sheet(
    financial_data: list[dict],
    balance_sheet_data: list[dict],
) -> list[dict]:
    """
    Merge TWSE income statement data and balance sheet data.

    Matching keys:
    - symbol
    - report_year
    - report_quarter
    """

    balance_map = {
        (
            item["symbol"],
            item["report_year"],
            item["report_quarter"],
        ): item
        for item in balance_sheet_data
    }

    merged = []

    for item in financial_data:

        key = (
            item["symbol"],
            item["report_year"],
            item["report_quarter"],
        )

        balance = balance_map.get(key, {})

        merged.append(
            {
                **item,
                "bvps": balance.get("bvps"),
            }
        )

    return merged