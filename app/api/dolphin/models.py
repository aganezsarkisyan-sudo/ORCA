"""Dolphin API models (DTOs).

Using dataclasses for simple, typed models as required.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Account:
    id: str
    name: str
    status: Optional[str] = None
    account_status: Optional[str] = None
    campaign_status: Optional[str] = None
    adset_status: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    balance: Optional[float] = None
    spend: Optional[float] = None
    cpl: Optional[float] = None
    created_at: Optional[datetime] = None


@dataclass(slots=True)
class Statistics:
    account_id: str
    date: str
    spend: Optional[float] = 0.0
    impressions: Optional[int] = 0
    link_click: Optional[int] = 0
    link_click_cpa: Optional[float] = 0.0
    fb_mobile_add_payment_info: Optional[int] = 0
    ctr: Optional[float] = 0.0
    cpm: Optional[float] = 0.0
