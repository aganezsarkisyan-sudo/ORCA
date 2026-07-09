"""Dolphin API client.

- Uses a single httpx.AsyncClient instance for connection pooling.
- Implements retries for specific status codes with exponential backoff.
- Logs every request/response, retries, and timings via loguru.
- Returns typed dataclass models defined in app.api.dolphin.models.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx
from loguru import logger

from app.api.dolphin import endpoints, exceptions, models
from app.core.config import settings


RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


class DolphinClient:
    """Async HTTP client for Dolphin Cloud API.

    Designed for dependency injection and reuse. The client can be used as an
    async context manager and will close its underlying httpx.AsyncClient on
    exit.
    """

    def __init__(self, base_url: str | None = None, api_token: str | None = None, timeout: float | None = None, retry_count: int | None = None) -> None:
        self.base_url = base_url or settings.dolphin_base_url
        self.api_token = api_token or settings.dolphin_api_token
        self.timeout = timeout or settings.dolphin_timeout
        self.retry_count = retry_count if retry_count is not None else settings.dolphin_retry_count

        headers = {"Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, headers=headers)
        self._closed = False

    async def __aenter__(self) -> "DolphinClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._closed:
            await self._client.aclose()
            self._closed = True

    async def _request_json(self, method: str, url: str, **kwargs: Any) -> Any:
        attempt = 0
        backoff_base = 0.5

        while True:
            attempt += 1
            try:
                start = time.monotonic()
                resp = await self._client.request(method, url, **kwargs)
                elapsed = time.monotonic() - start
                logger.debug("Dolphin request: {method} {url} status={code} time={time:.3f}s attempt={attempt}",
                             method=method, url=url, code=resp.status_code, time=elapsed, attempt=attempt)

                if resp.status_code in RETRY_STATUS_CODES and attempt < self.retry_count:
                    wait = backoff_base * (2 ** (attempt - 1))
                    logger.warning("Retrying Dolphin request {method} {url} in {wait}s due to status {code} (attempt {attempt})",
                                   method=method, url=url, wait=wait, code=resp.status_code, attempt=attempt)
                    await asyncio.sleep(wait)
                    continue

                # Handle status codes
                if resp.status_code == 401:
                    raise exceptions.AuthenticationError("Authentication failed")
                if resp.status_code == 429:
                    raise exceptions.RateLimitError("Rate limited by Dolphin API")
                if 500 <= resp.status_code <= 599:
                    raise exceptions.ServerError(f"Server error: {resp.status_code}")
                if 400 <= resp.status_code <= 499:
                    raise exceptions.ApiError(f"Client error: {resp.status_code}")

                # parse json
                try:
                    return resp.json()
                except json.JSONDecodeError as exc:
                    logger.exception("Failed to parse JSON from Dolphin response")
                    raise exceptions.ParsingError("Invalid JSON response") from exc

            except httpx.ReadTimeout as exc:
                logger.exception("Dolphin request timeout")
                if attempt < self.retry_count:
                    wait = backoff_base * (2 ** (attempt - 1))
                    logger.warning("Timeout — retrying in {wait}s (attempt {attempt})", wait=wait, attempt=attempt)
                    await asyncio.sleep(wait)
                    continue
                raise exceptions.TimeoutError("Request timed out") from exc
            except httpx.ConnectError as exc:
                logger.exception("Dolphin connection error")
                raise exceptions.ConnectionError("Connection error while connecting to Dolphin") from exc

    # High level API methods
    async def test_connection(self) -> bool:
        data = await self._request_json("GET", endpoints.TEST)
        # Expecting something like {"status":"ok"}
        return isinstance(data, dict) and data.get("status") in ("ok", "healthy")

    async def get_accounts(self) -> list[models.Account]:
        data = await self._request_json("GET", endpoints.BASE_ACCOUNTS)
        if not isinstance(data, list):
            raise exceptions.ParsingError("Expected list for accounts")

        result: list[models.Account] = []
        for item in data:
            try:
                acct = models.Account(
                    id=str(item.get("id")),
                    name=str(item.get("name", "")),
                    status=item.get("status"),
                    account_status=item.get("account_status"),
                    campaign_status=item.get("campaign_status"),
                    adset_status=item.get("adset_status"),
                    currency=item.get("currency"),
                    timezone=item.get("timezone"),
                    balance=float(item.get("balance")) if item.get("balance") is not None else None,
                    spend=float(item.get("spend")) if item.get("spend") is not None else None,
                    cpl=float(item.get("cpl")) if item.get("cpl") is not None else None,
                    created_at=None,
                )
                result.append(acct)
            except Exception as exc:
                logger.exception("Failed to parse account item")
                raise exceptions.ParsingError("Invalid account data") from exc
        return result

    async def get_account(self, account_id: str) -> models.Account:
        data = await self._request_json("GET", endpoints.ACCOUNT_BY_ID.format(account_id=account_id))
        if not isinstance(data, dict):
            raise exceptions.ParsingError("Expected object for account")
        try:
            return models.Account(
                id=str(data.get("id")),
                name=str(data.get("name", "")),
                status=data.get("status"),
                account_status=data.get("account_status"),
                campaign_status=data.get("campaign_status"),
                adset_status=data.get("adset_status"),
                currency=data.get("currency"),
                timezone=data.get("timezone"),
                balance=float(data.get("balance")) if data.get("balance") is not None else None,
                spend=float(data.get("spend")) if data.get("spend") is not None else None,
                cpl=float(data.get("cpl")) if data.get("cpl") is not None else None,
                created_at=None,
            )
        except Exception as exc:
            logger.exception("Failed to parse account detail")
            raise exceptions.ParsingError("Invalid account detail") from exc

    async def get_statistics(self, account_id: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[models.Statistics]:
        params: dict[str, str] = {}
        if account_id:
            params["account_id"] = account_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        data = await self._request_json("GET", endpoints.STATISTICS, params=params)
        if not isinstance(data, list):
            raise exceptions.ParsingError("Expected list for statistics")

        res: list[models.Statistics] = []
        for item in data:
            try:
                stat = models.Statistics(
                    account_id=str(item.get("account_id")),
                    date=str(item.get("date")),
                    spend=float(item.get("spend")) if item.get("spend") is not None else 0.0,
                    impressions=int(item.get("impressions")) if item.get("impressions") is not None else 0,
                    link_click=int(item.get("link_click")) if item.get("link_click") is not None else 0,
                    link_click_cpa=float(item.get("link_click_cpa")) if item.get("link_click_cpa") is not None else 0.0,
                    fb_mobile_add_payment_info=int(item.get("fb_mobile_add_payment_info")) if item.get("fb_mobile_add_payment_info") is not None else 0,
                    ctr=float(item.get("ctr")) if item.get("ctr") is not None else 0.0,
                    cpm=float(item.get("cpm")) if item.get("cpm") is not None else 0.0,
                )
                res.append(stat)
            except Exception as exc:
                logger.exception("Failed to parse statistic item")
                raise exceptions.ParsingError("Invalid statistics data") from exc
        return res

    async def get_status(self) -> dict[str, Any]:
        data = await self._request_json("GET", endpoints.STATUS)
        if not isinstance(data, dict):
            raise exceptions.ParsingError("Expected object for status")
        return data
