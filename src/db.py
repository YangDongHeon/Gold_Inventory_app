from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_PATH
from typing import Optional
import datetime

Base = declarative_base()
_engine = create_engine(f'sqlite:///{DB_PATH}', echo=False, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=_engine)

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

class DataManager:
    """Handles database operations using SQLAlchemy sessions."""
    def __init__(self):
        init_db()
        self.Session = SessionLocal

    def add_product(self, product: 'Product') -> 'Product':
        session = self.Session()
        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def update_product(self, product_id: int, **kwargs) -> 'Product':
        session = self.Session()
        from models import Product
        obj = session.query(Product).get(product_id)
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        session.commit()
        session.close()
        return obj

    def delete_product(self, product_id: int) -> bool:
        session = self.Session()
        from models import Product
        obj = session.query(Product).get(product_id)
        if not obj:
            session.close()
            return False
        paths = []
        if getattr(obj, "image_path", None):
            paths.append(obj.image_path)
        if getattr(obj, "extra_images", None):
            try:
                extra = json.loads(obj.extra_images) if isinstance(obj.extra_images, str) else obj.extra_images
                if extra:
                    paths.extend(extra)
            except Exception:
                pass
        session.delete(obj)
        session.commit()
        session.close()
        for p in paths:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass
        return True


    def get_products(self, filters: dict = None) -> list:
        """Retrieve products matching optional filters."""
        session = self.Session()
        from models import Product
        query = session.query(Product)
        if filters:
            for attr, val in filters.items():
                if hasattr(Product, attr) and val:
                    query = query.filter(getattr(Product, attr).like(f'%{val}%'))
        products = query.order_by(Product.is_favorite.desc(), Product.id.desc()).all()
        session.close()
        return products

    def get_product(self, product_id: int) -> Optional["Product"]:
        """Retrieve a single product by ID."""
        session = self.Session()
        from models import Product
        obj = session.get(Product, product_id)
        session.close()
        return obj

    def toggle_favorite(self, product_id: int) -> bool:
        session = self.Session()
        from models import Product
        obj = session.query(Product).get(product_id)
        if not obj:
            session.close()
            return False
        obj.is_favorite = not obj.is_favorite
        session.commit()
        session.close()
        return True

    def add_sales_record(self, sales_record: 'SalesRecord') -> 'SalesRecord':
        session = self.Session()
        session.add(sales_record)
        session.commit()
        session.refresh(sales_record)
        session.close()
        return sales_record

    def get_sales_records(self, filters: dict = None) -> list:
        """Retrieve sales records matching optional filters."""
        session = self.Session()
        from models import SalesRecord
        query = session.query(SalesRecord)
        if filters:
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            customer_name = filters.get('customer_name')
            product_name = filters.get('product_name')

            if start_date:
                query = query.filter(SalesRecord.sale_date >= start_date)
            if end_date:
                query = query.filter(SalesRecord.sale_date <= end_date)
            if customer_name:
                query = query.filter(SalesRecord.customer_name.like(f'%{customer_name}%'))
            if product_name:
                query = query.filter(SalesRecord.product_name.like(f'%{product_name}%'))

        sales_records = query.order_by(SalesRecord.sale_date.desc()).all()
        session.close()
        return sales_records

    def get_sales_record(self, record_id: int) -> Optional["SalesRecord"]:
        """Retrieve a single sales record by ID."""
        session = self.Session()
        from models import SalesRecord
        obj = session.get(SalesRecord, record_id)
        session.close()
        return obj

    def update_sales_record(self, record_id: int, **kwargs) -> "SalesRecord":
        session = self.Session()
        from models import SalesRecord
        obj = session.query(SalesRecord).get(record_id)
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        session.commit()
        session.close()
        return obj
