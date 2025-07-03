
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit, QCheckBox, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox
)
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from models import Product
from config import app_base_dir

PROJECT_ROOT = Path(app_base_dir())        # <project root> resolved by your helper
IMAGES_DIR   = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(exist_ok=True)            # create once if it doesn't exist

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

class ProductDialog(QDialog):
    def __init__(self, parent=None, product: Product | None = None):
        super().__init__(parent)
        self.setWindowTitle("상품 정보 수정" if product else "새 상품 등록")
        self.product = product
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)

        self.category_cb = QComboBox()
        self.category_cb.addItems(["", "E (귀걸이)", "R (반지)", "N (목걸이)", "B (팔찌)", "O (기타)"])
        self.supplier_edit = QLineEdit()
        self.supplier_no_edit = QLineEdit()
        self.product_code_edit = QLineEdit()
        self.name_edit = QLineEdit()

        self.karat_cb = QComboBox()
        self.karat_cb.addItems(["14K","18K","24K"])
        self.weight_spin = QDoubleSpinBox(); self.weight_spin.setMaximum(100000); self.weight_spin.setSuffix(" g")
        self.size_edit = QLineEdit()
        self.qb_edit = QLineEdit()
        self.qb_edit.setPlaceholderText("총QB수량")

        self.basic_left  = QLineEdit(); self.basic_left.setPlaceholderText("기본")
        self.basic_right = QLineEdit(); self.basic_right.setPlaceholderText("추가")
        basic_box = QHBoxLayout(); basic_box.addWidget(self.basic_left); basic_box.addWidget(QLabel("/")); basic_box.addWidget(self.basic_right)
        self.bulim_left  = QLineEdit(); self.bulim_left.setPlaceholderText("중앙")
        self.bulim_right = QLineEdit(); self.bulim_right.setPlaceholderText("보조")
        bulim_box = QHBoxLayout(); bulim_box.addWidget(self.bulim_left); bulim_box.addWidget(QLabel("/")); bulim_box.addWidget(self.bulim_right)
        self.labor_left  = QLineEdit(); self.labor_left.setPlaceholderText("중앙")
        self.labor_right = QLineEdit(); self.labor_right.setPlaceholderText("보조")
        labor_box = QHBoxLayout(); labor_box.addWidget(self.labor_left); labor_box.addWidget(QLabel("/")); labor_box.addWidget(self.labor_right)
        self.cubic_labor_edit    = QLineEdit()
        self.total_labor_edit    = QLineEdit()

        self.discontinued_cb = QComboBox(); self.discontinued_cb.addItems(["N","Y"])
        self.stock_spin = QSpinBox(); self.stock_spin.setMaximum(100000)

        self.img_path_edit = QLineEdit()
        browse_btn = QPushButton("사진 선택")
        browse_btn.clicked.connect(self._browse_image)
        img_layout = QHBoxLayout(); img_layout.addWidget(self.img_path_edit); img_layout.addWidget(browse_btn)

        self.notes_edit = QTextEdit()
        self.favorite_chk = QCheckBox("즐겨찾기")

        if self.product: self._populate()

        layout.addRow("품목", self.category_cb)
        layout.addRow("매입처명", self.supplier_edit)
        layout.addRow("매입처상품번호", self.supplier_no_edit)
        layout.addRow("상품번호", self.product_code_edit)
        layout.addRow("상품명*", self.name_edit)
        layout.addRow("함량", self.karat_cb)
        layout.addRow("중량", self.weight_spin)
        layout.addRow("사이즈", self.size_edit)
        layout.addRow("총QB수량", self.qb_edit)
        layout.addRow("기/추",        basic_box)
        layout.addRow("중/보 물림",    bulim_box)
        layout.addRow("중/보 공임",    labor_box)
        layout.addRow("큐빅 공임",      self.cubic_labor_edit)
        layout.addRow("총공임",         self.total_labor_edit)
        layout.addRow("단종", self.discontinued_cb)
        layout.addRow("재고수량", self.stock_spin)
        layout.addRow("대표 이미지", img_layout)
        layout.addRow(self.favorite_chk)
        layout.addRow("비고", self.notes_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장"); cancel_btn = QPushButton("취소")
        save_btn.clicked.connect(self.accept); cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn); btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def _populate(self):
        p = self.product
        for i in range(self.category_cb.count()):
            if self.category_cb.itemText(i).startswith(p.category):
                self.category_cb.setCurrentIndex(i)
                break
        self.name_edit.setText(p.name)
        self.supplier_edit.setText(p.supplier_name)
        self.supplier_no_edit.setText(p.supplier_item_no)
        self.product_code_edit.setText(p.product_code)
        self.karat_cb.setCurrentText(p.karat)
        self.weight_spin.setValue(p.weight_g)
        self.size_edit.setText(p.size)
        self.qb_edit.setText(str(p.total_qb_qty))

        left, right = split2(p.basic_extra)
        self.basic_left.setText(left)
        self.basic_right.setText(right)

        left, right = split2(p.mid_back_bulim)
        self.bulim_left.setText(left)
        self.bulim_right.setText(right)

        left, right = split2(p.mid_back_labor)
        self.labor_left.setText(left)
        self.labor_right.setText(right)

        self.cubic_labor_edit.setText(p.cubic_labor)
        self.total_labor_edit.setText(p.total_labor)
        self.discontinued_cb.setCurrentText("Y" if p.discontinued else "N")
        self.stock_spin.setValue(p.stock_qty)
        self.img_path_edit.setText(p.image_path)
        self.notes_edit.setPlainText(p.notes)
        self.favorite_chk.setChecked(p.is_favorite)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.img_path_edit.setText(path)

    def _import_image(self, src_path: str) -> str:
        """
        Copy *src_path* into <project>/images and return the destination
        path that should be written to the DB.  If the file is already in
        that folder, nothing is copied.
        """
        if not src_path:
            return ""

        src = Path(src_path).resolve()
        if not src.exists():
            return str(src)              # defensive--store what we got

        # Already inside images folder?
        if src.parent == IMAGES_DIR.resolve():
            return str(src)

        # Pick a non-colliding filename
        dest = IMAGES_DIR / src.name
        if dest.exists():
            base, ext = src.stem, src.suffix
            i = 1
            while (IMAGES_DIR / f"{base}_{i}{ext}").exists():
                i += 1
            dest = IMAGES_DIR / f"{base}_{i}{ext}"

        shutil.copy2(src, dest)          # copy with metadata
        return str(dest)                 # absolute; make relative if you prefer

    def get_product(self) -> Product | None:
        if self.exec_() != QDialog.Accepted: return None
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "오류", "상품명을 입력하세요."); return None
        
        cat_txt  = self.category_cb.currentText()
        category = cat_txt.split()[0] if cat_txt else ""

        raw_img_path = self.img_path_edit.text().strip()
        stored_img_path = self._import_image(raw_img_path)

        return Product(
            id=self.product.id if self.product else None,
            category=category,
            supplier_name=self.supplier_edit.text().strip(),
            supplier_item_no=self.supplier_no_edit.text().strip(),
            product_code=self.product_code_edit.text().strip(),
            name=self.name_edit.text().strip(),
            karat=self.karat_cb.currentText(),
            weight_g=self.weight_spin.value(),
            size=self.size_edit.text().strip(),
            total_qb_qty=self.qb_edit.text().strip(),
            basic_extra     = join2(self.basic_left.text(),  self.basic_right.text()),
            mid_back_bulim  = join2(self.bulim_left.text(),  self.bulim_right.text()),
            mid_back_labor  = join2(self.labor_left.text(),  self.labor_right.text()),
            cubic_labor     = self.cubic_labor_edit.text().strip(),
            total_labor     = self.total_labor_edit.text().strip(),
            discontinued=self.discontinued_cb.currentText()=="Y",
            stock_qty=self.stock_spin.value(),
            image_path=stored_img_path,
            extra_images=[],
            notes=self.notes_edit.toPlainText(),
            is_favorite=self.favorite_chk.isChecked()
        )
