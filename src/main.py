import sys
import os
from typing import List, Optional
from pathlib import Path
from datetime import date

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import threading
import webview
from uvicorn import Config, Server

from config import app_resource_path
from db import init_db
from models import Product, SalesRecord, ProductCreate, ProductUpdate, ProductInDB, SalesRecordCreate, SalesRecordUpdate, SalesRecordInDB
from repository import DataManager

app = FastAPI()
data_manager = DataManager()

# Serve images from the images directory
from fastapi import UploadFile, File
import aiofiles

# Product Endpoints
@app.post("/api/products/", response_model=ProductInDB)
def create_product(product: ProductCreate):
    # Convert Pydantic model to dict for DataManager
    product_data = product.model_dump(exclude_unset=True)
    new_product = data_manager.add_product(product_data)
    return new_product

@app.get("/api/products/", response_model=List[ProductInDB])
def read_products(
    category: Optional[str] = Query(None),
    supplier_name: Optional[str] = Query(None),
    supplier_item_no: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    product_code: Optional[str] = Query(None),
    discontinued: Optional[bool] = Query(None),
    is_favorite: Optional[bool] = Query(None),
):
    filters = {
        "category": category,
        "supplier_name": supplier_name,
        "supplier_item_no": supplier_item_no,
        "name": name,
        "product_code": product_code,
        "discontinued": discontinued,
        "is_favorite": is_favorite,
    }
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    products = data_manager.get_products(filters)
    return products

@app.get("/api/products/{product_id}", response_model=ProductInDB)
def read_product(product_id: int):
    product = data_manager.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/api/products/{product_id}", response_model=ProductInDB)
def update_product(product_id: int, product: ProductUpdate):
    updates = product.model_dump(exclude_unset=True)
    updated_product = data_manager.update_product(product_id, updates)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    if not data_manager.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.post("/api/products/{product_id}/toggle_favorite", response_model=ProductInDB)
def toggle_favorite(product_id: int):
    if not data_manager.toggle_favorite(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = data_manager.get_product(product_id)
    return updated_product

# Sales Record Endpoints
@app.post("/api/sales/", response_model=SalesRecordInDB)
def create_sales_record(sales_record: SalesRecordCreate):
    sales_record_data = sales_record.model_dump(exclude_unset=True)
    new_sales_record = data_manager.add_sales_record(sales_record_data)
    return new_sales_record

@app.get("/api/sales/", response_model=List[SalesRecordInDB])
def read_sales_records(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    customer_name: Optional[str] = Query(None),
    product_name: Optional[str] = Query(None),
):
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "customer_name": customer_name,
        "product_name": product_name,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    sales_records = data_manager.get_sales_records(filters)
    return sales_records

@app.get("/api/sales/{sales_id}", response_model=SalesRecordInDB)
def read_sales_record(sales_id: int):
    sales_record = data_manager.get_sales_record(sales_id)
    if sales_record is None:
        raise HTTPException(status_code=404, detail="Sales record not found")
    return sales_record

@app.put("/api/sales/{sales_id}", response_model=SalesRecordInDB)
def update_sales_record(sales_id: int, sales_record: SalesRecordUpdate):
    updates = sales_record.model_dump(exclude_unset=True)
    updated_sales_record = data_manager.update_sales_record(sales_id, updates)
    if updated_sales_record is None:
        raise HTTPException(status_code=404, detail="Sales record not found")
    return updated_sales_record

@app.delete("/api/sales/{sales_id}")
def delete_sales_record(sales_id: int):
    if not data_manager.delete_sales_record(sales_id):
        raise HTTPException(status_code=404, detail="Sales record not found")
    return {"message": "Sales record deleted successfully"}

def main():
    init_db()
    # Start the FastAPI server in a background thread
    config = Config(app, host="127.0.0.1", port=8000, log_level="info", workers=8)
    server = Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    # Open a native window for the frontend
    webview.create_window("Gold Inventory App", "http://127.0.0.1:8000")
    webview.start()
    # When window closes, shut down the server
    server.should_exit = True
    server_thread.join()

# Serve images from the images directory
@app.get("/images/{filename}")
async def serve_image(filename: str):
    image_path = app_resource_path('images', filename)
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@app.post("/api/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Ensure the 'images' directory exists
        images_dir = app_resource_path('images')
        images_dir.mkdir(exist_ok=True)

        file_path = images_dir / file.filename
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024):  # read in chunks
                await out_file.write(content)
        return {"filename": file.filename, "path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

# Mount static files for the frontend
app.mount("/", StaticFiles(directory=str(app_resource_path('src','frontend')), html=True), name="static")

if __name__ == '__main__':
    main()