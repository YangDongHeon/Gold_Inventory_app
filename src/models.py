from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from db import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, default='')
    name = Column(String, index=True, default='')
    supplier_name = Column(String, index=True, default='')
    supplier_item_no = Column(String, index=True, default='')
    product_code = Column(String, index=True, default='')
    karat = Column(String, default='14K')
    weight_g = Column(Float, default=0.0)
    size = Column(String, default='')
    total_qb_qty = Column(String, default='')
    basic_extra      = Column(String, default='')   # 기/추
    mid_back_bulim   = Column(String, default='')   # 중/보 물림
    mid_back_labor   = Column(String, default='')   # 중/보 공임
    cubic_labor      = Column(String, default='')   # 큐빅 공임
    total_labor      = Column(String, default='')   # 총공임
    discontinued = Column(Boolean, default=False)
    stock_qty = Column(Integer, default=0)
    image_path = Column(String, default='')
    extra_images = Column(JSON, default=[])
    notes = Column(String, default='')
    is_favorite = Column(Boolean, default=False)
