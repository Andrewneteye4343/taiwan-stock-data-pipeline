import time

import requests

TWSE_OPENAPI_BASE_URL = "https://openapi.twse.com.tw/v1"


def fetch_twse_api(
    endpoint: str,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> list[dict]:
    """
    Fetch data from TWSE OpenAPI with retry.

    Parameters
    ----------
    endpoint : str
        TWSE OpenAPI endpoint.

    timeout : int
        HTTP request timeout in seconds.

    max_retries : int
        Number of retries on transient failures.

    retry_delay : float
        Base delay in seconds between retries
        (exponential backoff: delay * 2^n).

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

    last_exception = None

    for attempt in range(max_retries):

        try:

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

        except (
            requests.RequestException,
            ValueError,
        ) as exc:

            last_exception = exc

            if attempt < max_retries - 1:

                delay = retry_delay * (2**attempt)

                print(
                    f"TWSE API retry {attempt + 1}/"
                    f"{max_retries} for {endpoint} "
                    f"after {delay:.0f}s: {exc}"
                )

                time.sleep(delay)

    if last_exception is None:
        raise RuntimeError(
            f"TWSE API request failed: {endpoint}"
        )

    raise last_exception
