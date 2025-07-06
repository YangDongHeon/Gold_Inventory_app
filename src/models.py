from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from db import Base
import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

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


class SalesRecord(Base):
    __tablename__ = 'sales_records'
    id = Column(Integer, primary_key=True, index=True)
    
    # Fields from the form
    customer_name = Column(String, index=True)
    sale_type = Column(String)
    return_reason = Column(String)
    purchase_market_price = Column(Integer)
    sale_market_price = Column(Integer)
    final_sale_price = Column(Integer)
    product_spplier = Column(String)
    product_name = Column(String, index=True)
    basic_extra = Column(String, default='')
    mid_back_bulim = Column(String, default='')
    
    karat_unit = Column(String)
    karat_g = Column(String)
    quantity = Column(Integer)
    color = Column(String)
    size = Column(String)
    
    
    main_stone_type = Column(String)
    main_stone_quantity = Column(Integer)
    main_stone_purchase_price = Column(Integer)
    main_stone_sale_price = Column(Integer)
    
    aux_stone_type = Column(String)
    aux_stone_quantity = Column(Integer)
    aux_stone_purchase_price = Column(Integer)
    aux_stone_sale_price = Column(Integer)

    notes = Column(String)
    sale_date = Column(Date, default=datetime.date.today, index=True)


# Pydantic models for API
class ProductBase(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_item_no: Optional[str] = None
    product_code: Optional[str] = None
    karat: Optional[str] = None
    weight_g: Optional[float] = None
    size: Optional[str] = None
    total_qb_qty: Optional[str] = None
    basic_extra: Optional[str] = None
    mid_back_bulim: Optional[str] = None
    mid_back_labor: Optional[str] = None
    cubic_labor: Optional[str] = None
    total_labor: Optional[str] = None
    discontinued: Optional[bool] = None
    stock_qty: Optional[int] = None
    image_path: Optional[str] = None
    extra_images: Optional[List[str]] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductInDB(ProductBase):
    id: int
    image_path: Optional[str] = Field(None, alias="image_path") # Ensure image_path is handled

    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Allow setting by field name

class SalesRecordBase(BaseModel):
    customer_name: Optional[str] = None
    sale_type: Optional[str] = None
    return_reason: Optional[str] = None
    purchase_market_price: Optional[int] = None
    sale_market_price: Optional[int] = None
    final_sale_price: Optional[int] = None
    product_spplier: Optional[str] = None
    product_name: Optional[str] = None
    basic_extra: Optional[str] = None
    mid_back_bulim: Optional[str] = None
    karat_unit: Optional[str] = None
    karat_g: Optional[str] = None
    quantity: Optional[int] = None
    color: Optional[str] = None
    size: Optional[str] = None
    main_stone_type: Optional[str] = None
    main_stone_quantity: Optional[int] = None
    main_stone_purchase_price: Optional[int] = None
    main_stone_sale_price: Optional[int] = None
    aux_stone_type: Optional[str] = None
    aux_stone_quantity: Optional[int] = None
    aux_stone_purchase_price: Optional[int] = None
    aux_stone_sale_price: Optional[int] = None
    notes: Optional[str] = None
    sale_date: Optional[datetime.date] = None

class SalesRecordCreate(SalesRecordBase):
    pass

class SalesRecordUpdate(SalesRecordBase):
    pass

class SalesRecordInDB(SalesRecordBase):
    id: int

    class Config:
        orm_mode = True