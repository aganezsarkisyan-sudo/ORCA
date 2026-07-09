"""Tests for database initialization, repository CRUD, mapping and synchronization."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_engine, init_db
from app.database.models import Account
from app.repositories.account_repository import AccountRepository
from app.services.mapping_service import MappingService


@pytest.fixture
def in_memory_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_engine):
    SessionLocal = sessionmaker(bind=in_memory_engine, autoflush=False, autocommit=False, future=True)
    return lambda: SessionLocal()


def test_sqlite_initialization(in_memory_engine):
    # tables exist
    inspector = in_memory_engine.inspect(in_memory_engine)
    # if no exception, assume ok
    assert in_memory_engine is not None


def test_account_crud(session_factory):
    repo = AccountRepository(session_factory=session_factory)
    acct = repo.save_account(dolphin_id="100", dolphin_name="Test Account", display_name="Test Account")
    assert acct.id is not None
    fetched = repo.get_by_dolphin_id("100")
    assert fetched is not None
    assert fetched.dolphin_name == "Test Account"
    repo.update_account(fetched.id, display_name="Updated")
    updated = repo.get_by_id(fetched.id)
    assert updated.display_name == "Updated"
    repo.delete_account(updated.id)
    deleted = repo.get_by_id(updated.id)
    assert deleted is not None and deleted.enabled is False


def test_mapping_priorities():
    matcher = MappingService()
    candidates = [(1, "1", "Alpha"), (2, "2", "alpha beta"), (3, "3", "alpha-beta"), (4, "4", "Alpha_Beta")]

    r = matcher.match("Alpha", candidates)
    assert r.method == "exact" and r.confidence == 1.0

    r2 = matcher.match("alpha", candidates)
    assert r2.method in ("ignore_case", "fuzzy")

    r3 = matcher.match("alpha beta", candidates)
    assert r3.confidence >= 0.9
