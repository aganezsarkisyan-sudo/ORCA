"""Database migrations and compatibility utilities."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import inspect
from loguru import logger
from app.database.database import get_engine


def apply_mapping_migration(engine: Engine | None = None) -> None:
    """Apply a non-destructive migration to introduce the new mapping tables/columns.

    - Adds new columns to existing account_mapping table (confidence, matching_method, created_at, updated_at) if missing.
    - Creates new excel_mapping table if it does not exist.

    This migration attempts to be idempotent and safe for sqlite.
    """
    engine = engine or get_engine()
    inspector = inspect(engine)

    # Add columns to account_mapping if missing
    if "account_mapping" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("account_mapping")}
        with engine.connect() as conn:
            if "confidence" not in cols:
                logger.info("Adding column 'confidence' to account_mapping")
                conn.execute(text("ALTER TABLE account_mapping ADD COLUMN confidence FLOAT"))
            if "matching_method" not in cols:
                logger.info("Adding column 'matching_method' to account_mapping")
                conn.execute(text("ALTER TABLE account_mapping ADD COLUMN matching_method VARCHAR(255)"))
            if "created_at" not in cols:
                logger.info("Adding column 'created_at' to account_mapping")
                conn.execute(text("ALTER TABLE account_mapping ADD COLUMN created_at DATETIME"))
            if "updated_at" not in cols:
                logger.info("Adding column 'updated_at' to account_mapping")
                conn.execute(text("ALTER TABLE account_mapping ADD COLUMN updated_at DATETIME"))

    # Create excel_mapping table if missing
    if "excel_mapping" not in inspector.get_table_names():
        logger.info("Creating excel_mapping table")
        create_sql = """
        CREATE TABLE IF NOT EXISTS excel_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            worksheet VARCHAR(255),
            anchor_cell VARCHAR(32),
            template_version VARCHAR(64),
            created_at DATETIME,
            updated_at DATETIME
        )
        """
        with engine.connect() as conn:
            conn.execute(text(create_sql))

    logger.info("Mapping migration applied successfully")
