
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFormLayout, QMessageBox
)
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from models import Product, SalesRecord
from .sales_record_dialog import SalesRecordDialog

class DetailDialog(QDialog):
    """Custom dialog for clearer, more readable product details."""
    def __init__(self, parent, product: Product):
        super().__init__(parent)
        self.product = product
        from PyQt5.QtGui import QFont
        self.setWindowTitle(product.name)
        self.setStyleSheet("QDialog {background: white;} QLabel {font-size:14px;}")
        # Main layout
        main_layout = QHBoxLayout(self)
        # ─── Left: Main + Extra Images ────────────
        img_layout = QVBoxLayout()
        if product.image_path and Path(product.image_path).exists():
            pix = QPixmap(product.image_path).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_img = QLabel()
            lbl_img.setPixmap(pix)
            lbl_img.setAlignment(Qt.AlignCenter)
            img_layout.addWidget(lbl_img)
        for extra in product.extra_images:
            if Path(extra).exists():
                pix2 = QPixmap(extra).scaled(
                    100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                lbl_extra = QLabel()
                lbl_extra.setPixmap(pix2)
                lbl_extra.setAlignment(Qt.AlignCenter)
                img_layout.addWidget(lbl_extra)
        main_layout.addLayout(img_layout)
        # ─── Right: Details Form ────────────────
        form = QFormLayout()
        font_bold = QFont()
        font_bold.setBold(True)
        # List of (label, value)
        fields = [
            ("품목",              product.category), 
            ("매입처(매입처상품번호)", f"{product.supplier_name} ({product.supplier_item_no})"),        
            ("상품명(상품번호)",  f"{product.name} ({product.product_code})"),
            ("함량",              product.karat),                 
            ("중량",              f"{product.weight_g} g"),       
            ("사이즈",            product.size),                 
            ("총QB수량",          product.total_qb_qty),      
            ("기/추",             product.basic_extra),        
            ("중/보 물림",        product.mid_back_bulim),    
            ("중/보 공임",        product.mid_back_labor),      
            ("큐빅 공임",         product.cubic_labor),        
            ("총공임",            product.total_labor),     
            ("단종",              "Y" if product.discontinued else "N"), 
            ("재고",              product.stock_qty),           
            ("비고",              product.notes or "-"),
        ]
        for key, val in fields:
            lbl_key = QLabel(f"{key}:")
            lbl_key.setFont(font_bold)
            lbl_val = QLabel(str(val))
            form.addRow(lbl_key, lbl_val)
        main_layout.addLayout(form)

        # ─── Button goes inside the *left* (image) column ─────────
        btn_layout = QHBoxLayout()
        btn_sell = QPushButton("판매")
        btn_sell.clicked.connect(self._sell_product)
        btn_ok = QPushButton("닫기")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_sell)
        btn_layout.addWidget(btn_ok)
        
        img_layout.addStretch()                   # push button to bottom if images are short
        img_layout.addLayout(btn_layout)

    def _sell_product(self):
        # Open sales record dialog prefilled with this product
        dlg = SalesRecordDialog(self, None, self.product)
        sales_record_data = dlg.get_sales_record_data()
        if sales_record_data:
            # Add and refresh
            self.parent().data.add_sales_record(sales_record_data)
            QMessageBox.information(self, "성공", "판매 기록이 추가되었습니다.")
            self.parent().load_sales()
            self.accept()
