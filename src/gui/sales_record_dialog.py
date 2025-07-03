import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTextEdit, QPushButton, QFormLayout, QGroupBox, QLabel, QMessageBox, QDateEdit
)
from models import SalesRecord

def join2(a: str, b: str) -> str:
    a = a.strip(); b = b.strip()
    if a and b:
        return f"{a}/{b}"
    elif a:
        return a
    elif b:
        return b
    else:
        return ""

def split2(s: str) -> tuple[str, str]:
    if "/" in s:
        left, right = s.split("/", 1)
        return left.strip(), right.strip()
    return s.strip(), ""

class SalesRecordDialog(QDialog):
    def __init__(self, parent=None, sales_record=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("판매 기록 수정" if sales_record else "판매 기록 등록")
        self.setMinimumWidth(600)
        # Removed setStyleSheet call as per instructions.
        self.sales_record = sales_record
        self.product = product
        self._build_ui()
        if sales_record:
            self._populate_ui()
        elif product:
            self._populate_from_product()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        from PyQt5.QtWidgets import QGroupBox

        # 기/추 and 중/보 물림 inputs as split fields
        self.basic_left = QLineEdit()
        self.basic_left.setPlaceholderText("기본")
        self.basic_left.setFrame(False)
        self.basic_right = QLineEdit()
        self.basic_right.setPlaceholderText("추가")
        self.basic_right.setFrame(False)
        basic_box = QHBoxLayout()
        basic_box.addWidget(self.basic_left)
        basic_box.addWidget(QLabel("/"))
        basic_box.addWidget(self.basic_right)

        self.bulim_left = QLineEdit()
        self.bulim_left.setPlaceholderText("중앙")
        self.bulim_left.setFrame(False)
        self.bulim_right = QLineEdit()
        self.bulim_right.setPlaceholderText("보조")
        self.bulim_right.setFrame(False)
        bulim_box = QHBoxLayout()
        bulim_box.addWidget(self.bulim_left)
        bulim_box.addWidget(QLabel("/"))
        bulim_box.addWidget(self.bulim_right)

        # Create all widgets
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setFrame(False)
        self.sale_type_cb = QComboBox()
        self.sale_type_cb.addItems(["판매", "반품"])
        self.return_reason_edit = QLineEdit()
        self.return_reason_edit.setFrame(False)
        self.product_spplier = QLineEdit()
        self.product_spplier.setFrame(False)
        self.product_name_edit = QLineEdit()
        self.product_name_edit.setFrame(False)
        self.karat_unit_cb = QComboBox()
        self.karat_unit_cb.addItems(["14K", "18K", "24K"])
        self.karat_g_edit = QLineEdit()
        self.karat_g_edit.setFrame(False)
        self.color_edit = QLineEdit()
        self.color_edit.setFrame(False)
        self.size_edit = QLineEdit()
        self.size_edit.setFrame(False)
        self.main_stone_type_edit = QLineEdit()
        self.aux_stone_type_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.sale_date_edit = QDateEdit(QDate.currentDate())
        self.sale_date_edit.setCalendarPopup(True)

        # Text inputs with unit labels (원 for prices, 개 for counts)
        self.purchase_price_edit = QLineEdit()
        self.purchase_price_edit.setFrame(False)
        purchase_box = QHBoxLayout()
        purchase_box.addWidget(self.purchase_price_edit)

        self.sale_price_edit = QLineEdit()
        self.sale_price_edit.setFrame(False)
        sale_box = QHBoxLayout()
        sale_box.addWidget(self.sale_price_edit)

        self.final_price_edit = QLineEdit()
        self.final_price_edit.setFrame(False)
        final_box = QHBoxLayout()
        final_box.addWidget(self.final_price_edit)

        self.quantity_edit = QLineEdit()
        self.quantity_edit.setFrame(False)
        self.main_quantity_edit = QLineEdit()
        self.main_quantity_edit.setFrame(False)
        self.main_purchase_price_edit = QLineEdit()
        self.main_purchase_price_edit.setFrame(False)
        self.main_sale_price_edit = QLineEdit()
        self.main_sale_price_edit.setFrame(False)
        self.aux_quantity_edit = QLineEdit()
        self.aux_quantity_edit.setFrame(False)
        self.aux_purchase_price_edit = QLineEdit()
        self.aux_purchase_price_edit.setFrame(False)
        self.aux_sale_price_edit = QLineEdit()
        self.aux_sale_price_edit.setFrame(False)


        # Vertically center-align text in all line edits
        for widget in [
            self.basic_left, self.basic_right,
            self.bulim_left, self.bulim_right,
            self.customer_name_edit, self.return_reason_edit,
            self.product_spplier, self.product_name_edit,
            self.karat_g_edit, self.color_edit, self.size_edit,
            self.purchase_price_edit, self.sale_price_edit, self.final_price_edit,
            self.quantity_edit, self.main_quantity_edit,
            self.main_purchase_price_edit, self.main_sale_price_edit,
            self.aux_quantity_edit, self.aux_purchase_price_edit, self.aux_sale_price_edit
        ]:
            widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Basic Info
        basic_group = QGroupBox("기본 정보")
        basic_form = QFormLayout()
        basic_form.addRow("판매일:", self.sale_date_edit)
        basic_form.addRow("고객명:", self.customer_name_edit)
        basic_form.addRow("구분:", self.sale_type_cb)
        basic_form.addRow("반품사유:", self.return_reason_edit)
        form = basic_form
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        basic_group.setLayout(basic_form)

        # Product Info
        product_group = QGroupBox("상품 정보")
        product_form = QFormLayout()
        product_form.addRow("매입처:", self.product_spplier)
        product_form.addRow("상품명:", self.product_name_edit)
        form = product_form
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        product_group.setLayout(product_form)

        # Price Info
        price_group = QGroupBox("가격 정보")
        price_form = QFormLayout()
        price_form.addRow("매입시세:", purchase_box)
        price_form.addRow("판매시세:", sale_box)
        price_form.addRow("판매가:", final_box)
        price_form.addRow("기/추:", basic_box)
        price_form.addRow("중/보 물림:", bulim_box)
        # Vertically center composite widgets in 가격 정보
        price_form.setAlignment(purchase_box, Qt.AlignVCenter)
        price_form.setAlignment(sale_box,     Qt.AlignVCenter)
        price_form.setAlignment(final_box,    Qt.AlignVCenter)
        price_form.setAlignment(basic_box,    Qt.AlignVCenter)
        price_form.setAlignment(bulim_box,    Qt.AlignVCenter)
        form = price_form
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        price_group.setLayout(price_form)

        # Stone Info
        stone_group = QGroupBox("석 정보")
        stone_group.setMinimumWidth(300)
        stone_form = QFormLayout()
        stone_form.addRow("함량/단위:", self.karat_unit_cb)
        stone_form.addRow("함량(g):", self.karat_g_edit)
        stone_form.addRow("수량:", self.quantity_edit)
        stone_form.addRow("색상:", self.color_edit)
        stone_form.addRow("사이즈:", self.size_edit)
        stone_form.addRow("메인석 종류:", self.main_stone_type_edit)
        stone_form.addRow("메인석 수량:", self.main_quantity_edit)
        stone_form.addRow("메인석 매입가:", self.main_purchase_price_edit)
        stone_form.addRow("메인석 판매가:", self.main_sale_price_edit)
        stone_form.addRow("보조석 종류:", self.aux_stone_type_edit)
        stone_form.addRow("보조석 수량:", self.aux_quantity_edit)
        stone_form.addRow("보조석 매입가:", self.aux_purchase_price_edit)
        stone_form.addRow("보조석 판매가:", self.aux_sale_price_edit)
        form = stone_form
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(8)
        stone_group.setLayout(stone_form)

        # Two-column layout: left holds basic, product, price; right holds stone
        container = QHBoxLayout()
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(30)
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(basic_group)
        left_vbox.addWidget(product_group)
        left_vbox.addWidget(price_group)
        left_vbox.addStretch()
        right_vbox = QVBoxLayout()
        right_vbox.addWidget(stone_group)
        right_vbox.addStretch()
        # wider left column
        container.addLayout(left_vbox, 2)
        container.addLayout(right_vbox, 1)
        main_layout.addLayout(container)

        # Notes
        notes_group = QGroupBox("비고")
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(self.notes_edit)
        notes_group.setLayout(notes_layout)
        main_layout.addWidget(notes_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("저장")
        cancel_btn = QPushButton("취소")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # Auto-fill from product
        if self.product:
            self._populate_from_product()

    def _populate_ui(self):
        record = self.sales_record
        self.customer_name_edit.setText(record.customer_name)
        self.sale_type_cb.setCurrentText(record.sale_type)
        self.return_reason_edit.setText(record.return_reason)
        # Populate QLineEdit fields instead of spinboxes for prices and quantities
        self.purchase_price_edit.setText(str(record.purchase_market_price))
        self.sale_price_edit.setText(str(record.sale_market_price))
        self.final_price_edit.setText(str(record.final_sale_price))
        self.product_spplier.setText(record.product_spplier)
        self.product_name_edit.setText(record.product_name)
        self.karat_unit_cb.setCurrentText(record.karat_unit)
        self.karat_g_edit.setText(record.karat_g)
        self.quantity_edit.setText(str(record.quantity))
        self.color_edit.setText(record.color)
        self.size_edit.setText(record.size)
        self.main_stone_type_edit.setText(record.main_stone_type)
        self.main_quantity_edit.setText(str(record.main_stone_quantity))
        self.main_purchase_price_edit.setText(str(record.main_stone_purchase_price))
        self.main_sale_price_edit.setText(str(record.main_stone_sale_price))
        self.aux_stone_type_edit.setText(record.aux_stone_type)
        self.aux_quantity_edit.setText(str(record.aux_stone_quantity))
        self.aux_purchase_price_edit.setText(str(record.aux_stone_purchase_price))
        self.aux_sale_price_edit.setText(str(record.aux_stone_sale_price))
        self.notes_edit.setPlainText(record.notes)
        self.sale_date_edit.setDate(QDate(record.sale_date))
        # populate split fields
        left, right = split2(record.basic_extra)
        self.basic_left.setText(left)
        self.basic_right.setText(right)
        left, right = split2(record.mid_back_bulim)
        self.bulim_left.setText(left)
        self.bulim_right.setText(right)

    def _populate_from_product(self):
        product = self.product
        self.product_spplier.setText(product.supplier_name)
        self.product_name_edit.setText(product.name)
        left, right = split2(product.basic_extra)
        self.basic_left.setText(left)
        self.basic_right.setText(right)
        left, right = split2(product.mid_back_bulim)
        self.bulim_left.setText(left)
        self.bulim_right.setText(right)

    def get_sales_record_data(self):
        if self.exec_() != QDialog.Accepted:
            return None

        # Validate numeric inputs
        try:
            purchase = int(self.purchase_price_edit.text().replace(',', '').strip() or 0)
            sale = int(self.sale_price_edit.text().replace(',', '').strip() or 0)
            final = int(self.final_price_edit.text().replace(',', '').strip() or 0)
            qty = int(self.quantity_edit.text().replace(',', '').strip() or 0)
            main_qty = int(self.main_quantity_edit.text().replace(',', '').strip() or 0)
            main_pp = int(self.main_purchase_price_edit.text().replace(',', '').strip() or 0)
            main_sp = int(self.main_sale_price_edit.text().replace(',', '').strip() or 0)
            aux_qty = int(self.aux_quantity_edit.text().replace(',', '').strip() or 0)
            aux_pp = int(self.aux_purchase_price_edit.text().replace(',', '').strip() or 0)
            aux_sp = int(self.aux_sale_price_edit.text().replace(',', '').strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "오류", "숫자 입력이 잘못되었습니다. 모든 숫자 필드를 확인해주세요.")
            return None

        return SalesRecord(
            id=self.sales_record.id if self.sales_record else None,
            customer_name=self.customer_name_edit.text().strip(),
            sale_type=self.sale_type_cb.currentText(),
            return_reason=self.return_reason_edit.text().strip(),
            purchase_market_price=purchase,
            sale_market_price=sale,
            final_sale_price=final,
            product_spplier=self.product_spplier.text().strip(),
            product_name=self.product_name_edit.text().strip(),
            karat_unit=self.karat_unit_cb.currentText(),
            karat_g=self.karat_g_edit.text().strip(),
            quantity=qty,
            color=self.color_edit.text().strip(),
            size=self.size_edit.text().strip(),
            main_stone_type=self.main_stone_type_edit.text().strip(),
            main_stone_quantity=main_qty,
            main_stone_purchase_price=main_pp,
            main_stone_sale_price=main_sp,
            aux_stone_type=self.aux_stone_type_edit.text().strip(),
            aux_stone_quantity=aux_qty,
            aux_stone_purchase_price=aux_pp,
            aux_stone_sale_price=aux_sp,
            basic_extra=join2(self.basic_left.text(), self.basic_right.text()),
            mid_back_bulim=join2(self.bulim_left.text(), self.bulim_right.text()),
            notes=self.notes_edit.toPlainText().strip(),
            sale_date=self.sale_date_edit.date().toPyDate()
        )

class SalesRecordDetailDialog(QDialog):
    """Dialog to view sales record details with clear section grouping."""
    def __init__(self, parent=None, record: SalesRecord=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("판매 기록 상세")
        self.setMinimumWidth(800)
        main_layout = QVBoxLayout(self)

        from PyQt5.QtWidgets import QGroupBox

        # 기본 정보
        basic_group = QGroupBox("기본 정보")
        basic_layout = QFormLayout()
        basic_layout.addRow("판매일:", QLabel(str(record.sale_date)))
        basic_layout.addRow("고객명:", QLabel(record.customer_name))
        basic_layout.addRow("구분:", QLabel(record.sale_type))
        basic_layout.addRow("반품사유:", QLabel(record.return_reason or "-"))
        basic_group.setLayout(basic_layout)

        # 상품 정보
        product_group = QGroupBox("상품 정보")
        product_layout = QFormLayout()
        product_layout.addRow("매입처:", QLabel(record.product_spplier))
        product_layout.addRow("상품명:", QLabel(record.product_name))
        product_group.setLayout(product_layout)

        # 가격 정보
        price_group = QGroupBox("가격 정보")
        price_layout = QFormLayout()
        price_layout.addRow("매입시세:", QLabel(f"{record.purchase_market_price:,} 원"))
        price_layout.addRow("판매시세:", QLabel(f"{record.sale_market_price:,} 원"))
        price_layout.addRow("판매가:", QLabel(f"{record.final_sale_price:,} 원"))
        price_layout.addRow("기/추:", QLabel(record.basic_extra.replace('/', ' / ')))
        price_layout.addRow("중/보 물림:", QLabel(record.mid_back_bulim.replace('/', ' / ')))
        price_group.setLayout(price_layout)

        # 석 정보
        stone_group = QGroupBox("석 정보")
        stone_layout = QFormLayout()
        stone_layout.addRow("수량:", QLabel(str(record.quantity)))
        stone_layout.addRow("색상:", QLabel(record.color))
        stone_layout.addRow("사이즈:", QLabel(record.size))
        stone_layout.addRow("메인석 종류:", QLabel(record.main_stone_type))
        stone_layout.addRow("메인석 수량:", QLabel(str(record.main_stone_quantity)))
        stone_layout.addRow("메인석 매입가:", QLabel(f"{record.main_stone_purchase_price:,} 원"))
        stone_layout.addRow("메인석 판매가:", QLabel(f"{record.main_stone_sale_price:,} 원"))
        stone_layout.addRow("보조석 종류:", QLabel(record.aux_stone_type))
        stone_layout.addRow("보조석 수량:", QLabel(str(record.aux_stone_quantity)))
        stone_layout.addRow("보조석 매입가:", QLabel(f"{record.aux_stone_purchase_price:,} 원"))
        stone_layout.addRow("보조석 판매가:", QLabel(f"{record.aux_stone_sale_price:,} 원"))
        stone_group.setLayout(stone_layout)

        # 비고
        notes_group = QGroupBox("비고")
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel(record.notes or "-"))
        notes_group.setLayout(notes_layout)

        # two-column container
        container = QHBoxLayout()
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(basic_group)
        left_vbox.addWidget(product_group)
        right_vbox = QVBoxLayout()
        right_vbox.addWidget(price_group)
        right_vbox.addWidget(stone_group)
        # Notes group should NOT be inside right_vbox
        container.addLayout(left_vbox)
        container.addLayout(right_vbox)
        main_layout.addLayout(container)

        # Notes group spans full width below both columns
        main_layout.addWidget(notes_group)

        # 닫기 버튼
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)