import requests


TWSE_OPENAPI_BASE_URL = "https://openapi.twse.com.tw/v1"


def fetch_twse_api(
    endpoint: str,
    timeout: int = 30,
) -> list[dict]:
    """
    Fetch data from TWSE OpenAPI.

    Parameters
    ----------
    endpoint : str
        TWSE OpenAPI endpoint.

    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    list[dict]
        JSON response records.

    Raises
    ------
    requests.HTTPError
        If the API returns an HTTP error.
    ValueError
        If the API response is not a list.
    """

    url = f"{TWSE_OPENAPI_BASE_URL}/{endpoint}"

    response = requests.get(
        url,
        timeout=timeout,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError(
            "TWSE API response must be a list."
        )

    return data