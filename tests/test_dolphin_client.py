"""Tests for DolphinClient retry and error handling.

Uses httpx.MockTransport to simulate Dolphin responses.
"""
from __future__ import annotations

import asyncio
import json
import pytest
import httpx

from app.api.dolphin.client import DolphinClient
from app.api.dolphin import exceptions


@pytest.mark.asyncio
async def test_successful_authentication():
    async def handler(request):
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as shared:
        client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
        # inject transport into underlying client for test
        client._client._transport = transport
        res = await client.test_connection()
        assert res is True


@pytest.mark.asyncio
async def test_401_raises_authentication_error():
    async def handler(request):
        return httpx.Response(401, json={"detail": "Unauthorized"})

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.AuthenticationError):
        await client._request_json("GET", "/ping")


@pytest.mark.asyncio
async def test_403_raises_api_error():
    async def handler(request):
        return httpx.Response(403, json={"detail": "Forbidden"})

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.ApiError):
        await client._request_json("GET", "/ping")


@pytest.mark.asyncio
async def test_404_raises_api_error():
    async def handler(request):
        return httpx.Response(404, json={"detail": "Not found"})

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.ApiError):
        await client._request_json("GET", "/ping")


@pytest.mark.asyncio
async def test_429_retries_and_raises_rate_limit():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, json={"detail": "Too many requests"})

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=3)
    client._client._transport = transport

    with pytest.raises(exceptions.RateLimitError):
        await client._request_json("GET", "/ping")
    assert calls >= 1


@pytest.mark.asyncio
async def test_500_retries_and_raises_server_error():
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(500, json={"detail": "Server error"})

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=2)
    client._client._transport = transport

    with pytest.raises(exceptions.ServerError):
        await client._request_json("GET", "/ping")
    assert calls >= 1


@pytest.mark.asyncio
async def test_timeout_raises_timeout_error():
    async def handler(request):
        raise httpx.ReadTimeout("timeout")

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.TimeoutError):
        await client._request_json("GET", "/ping")


@pytest.mark.asyncio
async def test_invalid_json_raises_parsing_error():
    async def handler(request):
        return httpx.Response(200, content=b"not-json")

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.ParsingError):
        await client._request_json("GET", "/ping")


@pytest.mark.asyncio
async def test_connection_error_raises_connection_error():
    async def handler(request):
        raise httpx.ConnectError("conn")

    transport = httpx.MockTransport(handler)
    client = DolphinClient(base_url="https://test/", api_token="tok", retry_count=1)
    client._client._transport = transport

    with pytest.raises(exceptions.ConnectionError):
        await client._request_json("GET", "/ping")
