from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    api_token = Column(String(255), nullable=True)
    base_url = Column(String(1024), nullable=True)
    excel_path = Column(String(2048), nullable=True)
    excel_sheet = Column(String(255), nullable=True)
    currency = Column(String(32), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    dolphin_id = Column(String(255), unique=True, nullable=False)
    dolphin_name = Column(String(1024), nullable=True)
    display_name = Column(String(1024), nullable=True)
    status = Column(String(64), nullable=True)
    account_status = Column(String(64), nullable=True)
    campaign_status = Column(String(64), nullable=True)
    adset_status = Column(String(64), nullable=True)
    currency = Column(String(32), nullable=True)
    timezone = Column(String(64), nullable=True)
    balance = Column(Float, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mappings = relationship("AccountMapping", back_populates="account")
    excel_mappings = relationship("ExcelMapping", back_populates="account")


class AccountMapping(Base):
    __tablename__ = "account_mapping"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    excel_block_name = Column(String(255), nullable=False)
    status_cell = Column(String(64), nullable=True)
    spend_cell = Column(String(64), nullable=True)
    cpl_cell = Column(String(64), nullable=True)
    leads_total_cell = Column(String(64), nullable=True)
    leads_unique_cell = Column(String(64), nullable=True)
    deps_cell = Column(String(64), nullable=True)
    avg_days_cell = Column(String(64), nullable=True)
    enabled = Column(Boolean, default=True)
    # Legacy timestamps (may be added by migration)
    confidence = Column(Float, nullable=True)
    matching_method = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="mappings")

    __table_args__ = (UniqueConstraint("account_id", "excel_block_name", name="uq_account_block"),)


class DailyStatistics(Base):
    __tablename__ = "daily_statistics"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(String(32), nullable=False)
    spend = Column(Float, nullable=True)
    cpl = Column(Float, nullable=True)
    clicks = Column(Integer, nullable=True)
    impressions = Column(Integer, nullable=True)
    payment_info = Column(Integer, nullable=True)
    status = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SyncHistory(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    accounts_processed = Column(Integer, default=0)
    accounts_success = Column(Integer, default=0)
    accounts_failed = Column(Integer, default=0)
    errors = Column(Text, nullable=True)


class AccountMappingDeprecated(Base):
    """Alias mapping to assist migrations if necessary."""
    __tablename__ = "account_mapping"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)


class ExcelMapping(Base):
    __tablename__ = "excel_mapping"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    worksheet = Column(String(255), nullable=True)
    anchor_cell = Column(String(32), nullable=False)
    # use template_name to identify the template (e.g., main_report, daily_report)
    template_name = Column(String(128), nullable=True)
    # keep legacy template_version if present for compatibility
    template_version = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="excel_mappings")

    __table_args__ = (
        UniqueConstraint("worksheet", "anchor_cell", name="uq_worksheet_anchor"),
        Index("ix_excelmapping_account", "account_id"),
    )
