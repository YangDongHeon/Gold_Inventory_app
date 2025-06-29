from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DB_PATH
from typing import Optional

Base = declarative_base()
_engine = create_engine(f'sqlite:///{DB_PATH}', echo=False, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=_engine)

def init_db():
    """Initialize the database, create tables if missing, and migrate schema for new columns."""
    # Ensure the database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    from . import models  # ensure Product table metadata is loaded
    Base.metadata.create_all(_engine)
    # Migrate existing table to include new columns
    with _engine.connect() as conn:
        existing = conn.exec_driver_sql("PRAGMA table_info(products)").fetchall()
        cols = [row[1] for row in existing]
        migration_columns = [
            ("size", "TEXT", "''"),
            ("total_qb_qty", "TEXT", "''"),
            ("labor_cost1", "REAL", "0.0"),
            ("labor_cost2", "REAL", "0.0"),
            ("set_no", "TEXT", "''"),
        ]
        for name, ctype, default in migration_columns:
            if name not in cols:
                conn.exec_driver_sql(f"ALTER TABLE products ADD COLUMN {name} {ctype} DEFAULT {default}")

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
        from .models import Product
        obj = session.query(Product).get(product_id)
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        session.close()
        return obj

    def delete_product(self, product_id: int) -> bool:
        session = self.Session()
        from .models import Product
        obj = session.query(Product).get(product_id)
        if not obj:
            session.close()
            return False
        session.delete(obj)
        session.commit()
        session.close()
        return True

    def get_products(self, filters: dict = None) -> list:
        """Retrieve products matching optional filters."""
        session = self.Session()
        from .models import Product
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
        from .models import Product
        obj = session.get(Product, product_id)
        session.close()
        return obj

    def toggle_favorite(self, product_id: int) -> bool:
        session = self.Session()
        from .models import Product
        obj = session.query(Product).get(product_id)
        if not obj:
            session.close()
            return False
        obj.is_favorite = not obj.is_favorite
        session.commit()
        session.close()
        return True
