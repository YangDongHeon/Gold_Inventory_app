from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from .db import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, default='')
    name = Column(String, index=True, default='')
    supplier_name = Column(String, index=True, default='')
    supplier_item_no = Column(String, index=True, default='')
    product_code = Column(String, unique=True, index=True, default='')
    karat = Column(String, default='14K')
    weight_g = Column(Float, default=0.0)
    size = Column(String, default='')
    total_qb_qty = Column(String, default='')
    labor_cost1 = Column(Float, default=0.0)
    labor_cost2 = Column(Float, default=0.0)
    set_no = Column(String, default='')
    discontinued = Column(Boolean, default=False)
    stock_qty = Column(Integer, default=0)
    image_path = Column(String, default='')
    extra_images = Column(JSON, default=[])
    notes = Column(String, default='')
    is_favorite = Column(Boolean, default=False)
