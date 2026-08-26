import time
import requests


URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"

SYMBOL = "2330"

PARAMS = {
    "ex_ch": f"tse_{SYMBOL}.tw",
    "json": "1",
    "delay": "0",
    "_": "1",
}


def fetch():
    response = requests.get(
        URL,
        params=PARAMS,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()["msgArray"][0]

    return {
        "time": data.get("t"),
        "z": data.get("z"),
        "p": data.get("p"),
        "s": data.get("s"),
        "tv": data.get("tv"),
        "v": data.get("v"),
    }


print("TWSE realtime field observation")
print(f"Symbol: {SYMBOL}")
print()
print(
    f"{'time':<10}"
    f"{'z':<12}"
    f"{'p':<5}"
    f"{'s':<5}"
    f"{'tv':<8}"
    f"{'v':<10}"
)
print("-" * 55)


for i in range(30):

    try:
        data = fetch()

        print(
            f"{str(data['time']):<10}"
            f"{str(data['z']):<12}"
            f"{str(data['p']):<5}"
            f"{str(data['s']):<5}"
            f"{str(data['tv']):<8}"
            f"{str(data['v']):<10}"
        )

    except Exception as exc:

        print(
            f"ERROR: {type(exc).__name__}: {exc}"
        )

    if i < 29:
        time.sleep(2)