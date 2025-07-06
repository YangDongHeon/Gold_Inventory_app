from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import SessionLocal, init_db
from models import Product, SalesRecord
from datetime import date

class DataManager:
    """Manages CRUD operations for products and sales records."""
    def __init__(self):
        init_db()
        self.Session = SessionLocal

    # --- Product Operations ---
    def add_product(self, product_data: Dict) -> Product:
        session = self.Session()
        product = Product(**product_data)
        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def update_product(self, product_id: int, updates: Dict) -> Optional[Product]:
        session = self.Session()
        product = session.get(Product, product_id)
        if not product:
            session.close()
            return None
        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def delete_product(self, product_id: int) -> bool:
        session = self.Session()
        product = session.get(Product, product_id)
        if not product:
            session.close()
            return False
        session.delete(product)
        session.commit()
        session.close()
        return True

    def get_products(self, filters: Dict[str, str] = None) -> List[Product]:
        session = self.Session()
        query = session.query(Product)
        if filters:
            for attr, val in filters.items():
                if hasattr(Product, attr) and val is not None:
                    if attr == "discontinued":
                        query = query.filter(Product.discontinued == (val.lower() == 'true' or val == 'Y'))
                    elif attr == "is_favorite":
                        if isinstance(val, bool):
                            query = query.filter(Product.is_favorite == val)
                        else:
                            query = query.filter(Product.is_favorite == (val.lower() == 'true' or val == '1'))
                    else:
                        query = query.filter(getattr(Product, attr).like(f'%{val}%'))
        products = query.order_by(Product.is_favorite.desc(), Product.id.desc()).all()
        session.close()
        return products

    def get_product(self, product_id: int) -> Optional[Product]:
        session = self.Session()
        product = session.get(Product, product_id)
        session.close()
        return product

    def toggle_favorite(self, product_id: int) -> bool:
        session = self.Session()
        product = session.get(Product, product_id)
        if not product:
            session.close()
            return False
        product.is_favorite = not product.is_favorite
        session.commit()
        session.close()
        return True

    # --- Sales Record Operations ---
    def add_sales_record(self, sales_record_data: Dict) -> SalesRecord:
        session = self.Session()
        sales_record = SalesRecord(**sales_record_data)
        session.add(sales_record)
        session.commit()
        session.refresh(sales_record)
        session.close()
        return sales_record

    def update_sales_record(self, record_id: int, updates: Dict) -> Optional[SalesRecord]:
        session = self.Session()
        sales_record = session.get(SalesRecord, record_id)
        if not sales_record:
            session.close()
            return None
        for key, value in updates.items():
            if hasattr(sales_record, key):
                setattr(sales_record, key, value)
        session.commit()
        session.refresh(sales_record)
        session.close()
        return sales_record

    def delete_sales_record(self, record_id: int) -> bool:
        session = self.Session()
        sales_record = session.get(SalesRecord, record_id)
        if not sales_record:
            session.close()
            return False
        session.delete(sales_record)
        session.commit()
        session.close()
        return True

    def get_sales_records(self, filters: Dict[str, str] = None) -> List[SalesRecord]:
        session = self.Session()
        query = session.query(SalesRecord)
        if filters:
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(SalesRecord.sale_date >= filters["start_date"])
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(SalesRecord.sale_date <= filters["end_date"])
            if "customer_name" in filters and filters["customer_name"]:
                query = query.filter(SalesRecord.customer_name.like(f'%{filters["customer_name"]}'))
            if "product_name" in filters and filters["product_name"]:
                query = query.filter(SalesRecord.product_name.like(f'%{filters["product_name"]}'))

        sales_records = query.order_by(SalesRecord.sale_date.desc()).all()
        session.close()
        return sales_records

    def get_sales_record(self, record_id: int) -> Optional[SalesRecord]:
        session = self.Session()
        sales_record = session.get(SalesRecord, record_id)
        session.close()
        return sales_record