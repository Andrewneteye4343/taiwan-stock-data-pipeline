from src.api.twse import fetch_twse_api


def main():
    endpoint = "opendata/t187ap06_L_ci"

    data = fetch_twse_api(endpoint)

    print(f"Total record count: {len(data)}")
    print()

    rows = [
        row
        for row in data
        if row.get("公司代號") == "2330"
    ]

    print(f"2330 record count: {len(rows)}")
    print()

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()