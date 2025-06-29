from typing import List, Optional, Dict
from .db import SessionLocal, init_db
from .models import Product

class ProductRepository:
    """Repository for CRUD operations on products."""
    def __init__(self):
        init_db()
        self.Session = SessionLocal

    def add(self, product_data: Dict) -> Product:
        session = self.Session()
        product = Product(**product_data)
        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def update(self, product_id: int, updates: Dict) -> Optional[Product]:
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

    def delete(self, product_id: int) -> bool:
        session = self.Session()
        product = session.get(Product, product_id)
        if not product:
            session.close()
            return False
        session.delete(product)
        session.commit()
        session.close()
        return True

    def list(self, filters: Dict[str, str] = None) -> List[Product]:
        session = self.Session()
        query = session.query(Product)
        if filters:
            for attr, val in filters.items():
                if hasattr(Product, attr) and val:
                    query = query.filter(getattr(Product, attr).like(f'%{val}%'))
        products = query.order_by(Product.is_favorite.desc(), Product.id.desc()).all()
        session.close()
        return products

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
