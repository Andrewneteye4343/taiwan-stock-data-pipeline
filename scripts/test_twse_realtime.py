import json

import requests


TWSE_URL = (
    "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
)


def get_stock_realtime(symbol: str) -> dict:
    """
    Query TWSE public market information for one stock.

    This script is for personal learning / testing only.
    It does not persist or redistribute market data.
    """

    params = {
        "ex_ch": f"tse_{symbol}.tw",
        "json": "1",
        "delay": "0",
    }

    response = requests.get(
        TWSE_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    symbol = "2330"

    data = get_stock_realtime(symbol)

    print("HTTP request successful.")
    print()
    print("Raw JSON:")
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
    )
