"""Shared HTTP behaviour: retries, timeouts and identifiable user agent."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = (
    "kerala2040/1.0 "
    "(research; https://github.com/abhijith-sivaprasadan/kerala2040)"
)


def build_session(*, retries: int = 4, backoff: float = 0.7) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def checked(response: requests.Response) -> requests.Response:
    response.raise_for_status()
    return response
