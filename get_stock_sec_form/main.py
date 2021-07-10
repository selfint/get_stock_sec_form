import requests
from flask import Request, Response
from requests.adapters import HTTPAdapter
from sec_edgar_downloader._constants import (
    DATE_FORMAT_TOKENS,
    DEFAULT_AFTER_DATE,
    DEFAULT_BEFORE_DATE,
    MAX_RETRIES,
    SEC_EDGAR_RATE_LIMIT_SLEEP_INTERVAL,
    SEC_EDGAR_SEARCH_API_ENDPOINT,
)
from sec_edgar_downloader._utils import (
    EdgarSearchApiError,
    FilingMetadata,
    build_filing_metadata_from_hit,
    form_request_payload,
)
from urllib3.util.retry import Retry

HEADERS = {"User-Agent": "Vale selfint@gmail.com", "Accept-Encoding": "gzip, deflate"}


def get_stock_sec_form(request: Request) -> Response:
    """
    HTTP Cloud Function. Fetch SEC form of a stock.

    Returns the HTML of the requested form as the response.
    """

    print(f"Got request json: {request.json}")
    stock = request.json["stock"]
    form = request.json["form"]

    form_content = _get_stock_sec_form_html(stock.upper(), form.upper())
    return Response(form_content)


def _get_stock_sec_form_html(stock: str, form: str) -> str:
    """Download latest form for stock and return the form's HTML content"""

    url_metadata = _get_filing_url(form.upper(), stock.upper())
    url = url_metadata.full_submission_url

    print(f"Fetching form from url '{url}'")
    content = requests.get(url, headers=HEADERS).text

    print(f"Got content ({len(content)} chars)")
    return content


def _get_filing_url(
    filing_type: str,
    ticker_or_cik: str,
) -> FilingMetadata:
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=SEC_EDGAR_RATE_LIMIT_SLEEP_INTERVAL,
        status_forcelist=[403, 500, 502, 503, 504],
    )
    client = requests.Session()
    client.mount("http://", HTTPAdapter(max_retries=retries))
    client.mount("https://", HTTPAdapter(max_retries=retries))
    try:
        payload = form_request_payload(
            ticker_or_cik,
            [filing_type],
            DEFAULT_AFTER_DATE.strftime(DATE_FORMAT_TOKENS),
            DEFAULT_BEFORE_DATE.strftime(DATE_FORMAT_TOKENS),
            0,
            "",
        )
        resp = client.post(
            SEC_EDGAR_SEARCH_API_ENDPOINT,
            json=payload,
            headers=HEADERS,
        )
        resp.raise_for_status()
        search_query_results = resp.json()

        if "error" in search_query_results:
            try:
                root_cause = search_query_results["error"]["root_cause"]
                if not root_cause:  # pragma: no cover
                    raise ValueError

                error_reason = root_cause[0]["reason"]
                raise EdgarSearchApiError(
                    f"Edgar Search API encountered an error: {error_reason}. "
                    f"Request payload: {payload}"
                )
            except (ValueError, KeyError):  # pragma: no cover
                raise EdgarSearchApiError(
                    "Edgar Search API encountered an unknown error. "
                    f"Request payload:\n{payload}"
                )

        hit = search_query_results["hits"]["hits"][0]

        metadata = build_filing_metadata_from_hit(hit)

    finally:
        client.close()

    return metadata
