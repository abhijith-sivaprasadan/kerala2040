"""Generic data.gov.in Open Government Data API client."""

from __future__ import annotations

import os
from typing import Any, Self

import pandas as pd
from requests import Session

from kerala2040.provenance import utc_now_iso
from kerala2040.sources.http import build_session, checked

API_ROOT = "https://api.data.gov.in/resource"


class OGDClient:
    """Small paginated client; resource IDs stay in source configuration."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        session: Session | None = None,
        timeout: float = 45.0,
    ) -> None:
        self.api_key = api_key or os.getenv("DATA_GOV_API_KEY")
        if not self.api_key:
            raise ValueError(
                "data.gov.in requires an API key. Set DATA_GOV_API_KEY; "
                "never commit the key."
            )
        self.session = session or build_session()
        self._owns_session = session is None
        self.timeout = timeout

    def close(self) -> None:
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def fetch_resource(
        self,
        resource_id: str,
        *,
        filters: dict[str, str | int | float] | None = None,
        page_size: int = 500,
        max_records: int | None = None,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        if not 1 <= page_size <= 1000:
            raise ValueError("page_size must be between 1 and 1000")
        endpoint = f"{API_ROOT}/{resource_id}"
        offset = 0
        records: list[dict[str, Any]] = []
        raw_pages = 0

        while True:
            params: dict[str, Any] = {
                "api-key": self.api_key,
                "format": "json",
                "offset": offset,
                "limit": page_size,
            }
            for name, value in (filters or {}).items():
                params[f"filters[{name}]"] = value

            response = checked(self.session.get(endpoint, params=params, timeout=self.timeout))
            payload = response.json()
            page = payload.get("records", [])
            if not isinstance(page, list):
                raise TypeError("OGD response 'records' field is not a list")
            raw_pages += 1
            records.extend(page)

            if max_records is not None and len(records) >= max_records:
                records = records[:max_records]
                break
            if len(page) < page_size:
                break
            offset += page_size

        metadata = {
            "source_id": "data_gov_in_ogd",
            "resource_id": resource_id,
            "endpoint": endpoint,
            "filters": filters or {},
            "retrieved_at_utc": utc_now_iso(),
            "pages": raw_pages,
            "records": len(records),
        }
        return pd.DataFrame.from_records(records), metadata
