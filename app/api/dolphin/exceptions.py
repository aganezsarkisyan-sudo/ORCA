"""Dolphin API exceptions.

Custom exceptions used across the Dolphin integration.
"""
from __future__ import annotations

from typing import Optional


class DolphinError(Exception):
    """Base class for Dolphin-related errors."""


class AuthenticationError(DolphinError):
    """Raised when authentication fails (401)."""


class ConnectionError(DolphinError):
    """Raised when a network connection error occurs."""


class TimeoutError(DolphinError):
    """Raised when a request times out."""


class RateLimitError(DolphinError):
    """Raised when rate-limited by the API (429)."""


class ApiError(DolphinError):
    """Generic API error for 4xx responses."""


class ServerError(DolphinError):
    """Raised for 5xx server errors."""


class ParsingError(DolphinError):
    """Raised when the response cannot be parsed as expected."""
