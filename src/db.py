from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_PATH
from typing import Optional
import datetime

Base = declarative_base()
_engine = create_engine(f'sqlite:///{DB_PATH}', echo=False, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database, create tables if missing, and migrate schema for new columns."""
    # Ensure the database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    import models  # ensure Product and SalesRecord table metadata is loaded
    Base.metadata.create_all(_engine)
    # Migrate existing table to include new columns
    with _engine.connect() as conn:
        existing = conn.exec_driver_sql("PRAGMA table_info(products)").fetchall()
        cols = [row[1] for row in existing]
        migration_columns = [
            ("size",           "TEXT", "''"),
            ("total_qb_qty",   "TEXT", "''"),
            ("basic_extra",    "TEXT", "''"),
            ("mid_back_bulim", "TEXT", "''"),
            ("mid_back_labor", "TEXT", "''"),
            ("cubic_labor",    "TEXT", "''"),
            ("total_labor",    "TEXT", "''"),
            # SalesRecord fields
            # will add to sales_records table
            ("basic_extra",    "TEXT", "''"),
            ("mid_back_bulim", "TEXT", "''"),
        ]
        # Only apply to products table
        for name, ctype, default in migration_columns:
            if name not in cols and name not in ("basic_extra", "mid_back_bulim"):
                conn.exec_driver_sql(f"ALTER TABLE products ADD COLUMN {name} {ctype} DEFAULT {default}")
        # Migrate sales_records table for new columns
        existing_sr = conn.exec_driver_sql("PRAGMA table_info(sales_records)").fetchall()
        cols_sr = [row[1] for row in existing_sr]
        for name, ctype, default in [("basic_extra", "TEXT", "''"), ("mid_back_bulim", "TEXT", "''")]:
            if name not in cols_sr:
                conn.exec_driver_sql(f"ALTER TABLE sales_records ADD COLUMN {name} {ctype} DEFAULT {default}")
