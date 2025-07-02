import sys, json
from pathlib import Path
from typing import Dict
import shutil
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont
# from PyQt5.QtWidgets ... (unchanged)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCheckBox, QSizePolicy, QAbstractSpinBox
)
# Additional imports for DetailDialog
from models import Product
from PyQt5.QtWidgets import QDialog, QFormLayout
from config import app_base_dir, app_resource_path
# ─── Paths ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(app_base_dir())        # <project root> resolved by your helper
IMAGES_DIR   = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(exist_ok=True)            # create once if it doesn't exist

def join2(a: str, b: str) -> str:
    a = a.strip(); b = b.strip()
    return f"{a}/{b}" if a or b else ""

def split2(s: str) -> tuple[str, str]:
    if "/" in s:
        left, right = s.split("/", 1)
        return left.strip(), right.strip()
    return s.strip(), ""

def _fmt_slash(val: str) -> str:
    return val.replace("/", "\n") if val else val

class DetailDialog(QDialog):
    """Custom dialog for clearer, more readable product details."""
    def __init__(self, parent, product: Product):
        super().__init__(parent)
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
        btn_ok = QPushButton("닫기")
        btn_ok.clicked.connect(self.accept)
        img_layout.addStretch()                   # push button to bottom if images are short
        img_layout.addWidget(btn_ok, alignment=Qt.AlignHCenter)
# Ensure QApplication is imported for combo box style setting
from PyQt5.QtWidgets import QApplication
from db import DataManager
from models import Product
from functools import partial 

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.IMG_SIDE   = 80    
        self.CELL_HEIGHT = self.IMG_SIDE
        self.IMAGE_SIZE  = 300 
        self._init_icons()
        self.setWindowTitle("GOLD MANAGER")
        self.data = DataManager()
        self._build_ui()
        self.load_products()

    def _init_icons(self):
        from PyQt5.QtCore import Qt
        icon_dir = Path(app_resource_path('./src/icons'))

        def _scaled_icon(path: Path, size: int = 24) -> QIcon:
            pm = QPixmap(str(path)).scaled(
                size, size,  Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            return QIcon(pm)

        self.STAR_ON  = _scaled_icon(icon_dir / "star_on.png")
        self.STAR_OFF = _scaled_icon(icon_dir / "star_off.png")
        self.EDIT_IC  = _scaled_icon(icon_dir / "pencil.png")

    def _apply_column_widths(self):
        """이미지 열은 고정폭, 나머지는 내용 길이대로 자동 폭"""
        hdr = self.table.horizontalHeader()
        img_col  = 1
        name_col = 5
        fav_col  = self.table.columnCount() - 2
        edit_col = self.table.columnCount() - 1
        # ── 고정폭 열 ──────────────────────────
        for col, width in (
            (img_col,  self.IMG_SIDE + 6),   # 이미지 + padding
            (fav_col,  90),
            (edit_col, 40),
        ):
            hdr.setSectionResizeMode(col, QHeaderView.Fixed)
            self.table.setColumnWidth(col, width)
        # ── 나머지 열 : 내용 길이에 따라 폭 조정 ──
        for col in range(self.table.columnCount()):
            if col == name_col:
                hdr.setSectionResizeMode(col, QHeaderView.Stretch)
            elif col not in (img_col, fav_col, edit_col):
                hdr.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        # 마지막 열이 임의로 늘어나는 것 방지 (Stretch 대상은 상품명만)
        hdr.setStretchLastSection(False)

    def _build_ui(self):
        central = QWidget(); vbox = QVBoxLayout(central)

        # search bar
        search_h = QHBoxLayout()
        self.f_widgets: Dict[str, QLineEdit|QComboBox] = {}
        cat_cb = QComboBox(); cat_cb.addItems(["","E","R","N","B","O"])
        cat_cb.setEditable(True)
        cat_cb.lineEdit().setReadOnly(True)
        cat_cb.lineEdit().setPlaceholderText("품목")
        cat_cb.setFixedWidth(80)
        cat_cb.setToolTip("품목 필터")
        # Removed setStyle(QApplication.style()) to allow stylesheet to apply
        self.f_widgets["category"]=cat_cb; search_h.addWidget(cat_cb)

        sup_edit = QLineEdit(); sup_edit.setPlaceholderText("매입처명"); self.f_widgets["supplier_name"]=sup_edit; search_h.addWidget(sup_edit)
        sup_no = QLineEdit(); sup_no.setPlaceholderText("매입처상품번호"); self.f_widgets["supplier_item_no"]=sup_no; search_h.addWidget(sup_no)
        name_edit = QLineEdit(); name_edit.setPlaceholderText("상품명"); self.f_widgets["name"]=name_edit; search_h.addWidget(name_edit)
        code_edit = QLineEdit(); code_edit.setPlaceholderText("상품번호"); self.f_widgets["product_code"]=code_edit; search_h.addWidget(code_edit)
        
        disc_cb = QComboBox(); disc_cb.addItems(["","Y","N"])
        disc_cb.setEditable(True)
        disc_cb.lineEdit().setReadOnly(True)
        disc_cb.lineEdit().setPlaceholderText("단종")
        disc_cb.setFixedWidth(80)
        disc_cb.setToolTip("단종")
        # Removed setStyle(QApplication.style()) to allow stylesheet to apply
        self.f_widgets["discontinued"]=disc_cb; search_h.addWidget(disc_cb)

        search_btn = QPushButton("검색"); search_btn.clicked.connect(lambda: self.load_products(self._filters())); search_h.addWidget(search_btn)
        reset_btn = QPushButton("메인으로"); reset_btn.clicked.connect(self._show_all); search_h.addWidget(reset_btn) 
        
        vbox.addLayout(search_h)

        # --- Global (buttons / tabs / combobox) -------------------------------
        GLOBAL_CSS = """
        /* ─── PushButton ─────────────────────────── */
        QPushButton {
            background: #1890ff;          /* 포인트 블루 */
            color:       #ffffff;
            border:      none;
            border-radius: 4px;
            padding: 4px 12px;
            font-weight: 500;
        }
        QPushButton:hover   { background: #40a9ff; }
        QPushButton:pressed { background: #096dd9; }
        QPushButton:disabled{
            background: #dcdcdc;
            color:      #9f9f9f;
        }

        /* ─── Tab Bar (이미지 / 목록) ─────────────── */
        QTabBar::tab {
            background: #f5f5f5;
            border: 1px solid #d0d0d0;
            border-bottom: none;
            padding: 6px 14px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 2px solid #1890ff;
            font-weight: 600;
        }

        /* ─── ComboBox ───────────────────────────── */
        QComboBox {
            background: #1890ff;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 4px 12px;
            font-weight: 500;
        }
        QComboBox:hover {
            background: #40a9ff;
        }
        QComboBox:pressed {
            background: #096dd9;
        }
        QComboBox:disabled {
            background: #dcdcdc;
            color: #9f9f9f;
        }
        """

        COMMON_CSS = """
        /* -------- Views -------- */
        QTableWidget, QListWidget {
            background:#ffffff;
            gridline-color:#d0d0d0;
        }
        QHeaderView::section {
            background:#f0f0f0;
            padding:4px;
            border:1px solid #dadada;
        }
        QTableWidget::item:selected,
        QListWidget::item:selected {
            background:#e6f4ff;
            color:#212121;
        }

        /* -------- Tabs -------- */
        QTabWidget::pane {
            border:none;
            background:#ffffff;
        }
        QTabBar::tab {
            background:#f7f7f7;
            padding:6px 14px;
            border:1px solid #d0d0d0;
            border-bottom:none;
            border-radius:4px 4px 0 0;
            margin-right:2px;
        }
        QTabBar::tab:selected {
            background:#e6f4ff;
            font-weight:bold;
        }

        /* -------- Inputs -------- */
        QLineEdit, QComboBox {
            background:#ffffff;
            border:1px solid #d0d0d0;
            padding:3px 6px;
            border-radius:4px;
            color:#212121;
        }

        /* keep line‑edit and spin‑box text aligned */
        QSpinBox, QDoubleSpinBox {
            padding: 3px 6px;    /* text padding only – no border/background overrides */
        }

        /* -------- Buttons -------- */
        QPushButton {
            background:#1890ff;
            color:#ffffff;
            border:none;
            border-radius:4px;
            padding:6px 14px;
        }
        QPushButton:hover     { background:#40a9ff; }
        QPushButton:pressed   { background:#096dd9; }
        /*  disabled 색상을 파란계열로 유지 */
        QPushButton:disabled  { background:#d6e4ff; color:#8c8c8c; }

        /* 작은(셀) 버튼 – 아이콘만 쓰므로 투명, hover 효과만 */
        QPushButton[cellBtn="true"] {
            background:transparent;
            padding:0;
        }
        QPushButton[cellBtn="true"]:hover {
            background:#1890ff11;
            border-radius:4px;
        }
        """

        # tabs
        self.tabs = QTabWidget()
        self.image_list = QListWidget()
        self.image_list.setFlow(QListWidget.LeftToRight)
        self.image_list.setResizeMode(QListWidget.Adjust)   # ← ★ 중요: 크기 변경 시 재배치
        self.image_list.setWrapping(True)                   # ← 행이 가득 차면 자동 줄바꿈
        # 이미지 리스트

        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(self.IMAGE_SIZE,self.IMAGE_SIZE))
        self.image_list.setSpacing(15)
        self.image_list.itemDoubleClicked.connect(self._show_popup)
        self.tabs.addTab(self.image_list, "이미지")

        self.table = QTableWidget()
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideNone)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Dynamically set column count and headers
        headers = [
            "ID","이미지","품목","매입처","매입처상품번호","상품명","상품번호","함량","중량(g)","사이즈",
            "총QB수량","기/추","중/보 물림","중/보 공임","큐빅 공임","총공임","단종","재고",
            "즐겨찾기","수정"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.BTN_SIZE   = 32                    # 버튼 한 변 (px)
        self.ICON_SIZE  = 24                    # 아이콘 한 변 (px)
        self.COL_WIDTH  = self.BTN_SIZE + 6          # 좌우 여백 고려 (예: 38px)

        header = self.table.horizontalHeader()
        # Set all columns to Interactive except 이미지 col which should stretch
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        # 이미지 column (index 1) takes all extra horizontal space
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        # 열 너비: 이미지 120px, 버튼 38px
        self.table.setColumnWidth(1, 120)  # 이미지 칼럼 넓게
        # The following widths will be overridden in _apply_column_widths()
        header.setStretchLastSection(False)
        # Set row height to accommodate 120px-tall images plus 20px vertical padding
        ROW_PADDING = 6
        self.table.verticalHeader().setDefaultSectionSize(self.CELL_HEIGHT + ROW_PADDING)
        # Keep rows at a fixed height to prevent collapse
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.cellClicked.connect(self._table_click)
        self.table.itemDoubleClicked.connect(self._row_dbl_clicked)
        self._apply_column_widths()
        self.tabs.addTab(self.table, "목록")

        vbox.addWidget(self.tabs)

        # action buttons
        btn_h = QHBoxLayout()
        add_b = QPushButton("추가"); add_b.clicked.connect(self._add); btn_h.addWidget(add_b)
        #edit_b = QPushButton("수정"); edit_b.clicked.connect(self._edit); btn_h.addWidget(edit_b)
        del_b = QPushButton("삭제"); del_b.clicked.connect(self._delete); btn_h.addWidget(del_b)
        #fav_b = QPushButton("즐겨찾기 전환"); fav_b.clicked.connect(self._toggle_fav); btn_h.addWidget(fav_b)
        btn_fav_only = QPushButton("즐겨찾기 보기"); btn_fav_only.clicked.connect(self._show_favs); btn_h.addWidget(btn_fav_only)

        vbox.addLayout(btn_h)

        self.setCentralWidget(central)
        # 전역 스타일시트: 공통 + 테이블/리스트용
        self.setStyleSheet(GLOBAL_CSS + COMMON_CSS)

    def _filters(self):
        d = {}
        for k, w in self.f_widgets.items():
            val = w.currentText() if isinstance(w, QComboBox) else w.text()
            val = val.strip()
            if val:                       # 빈 값 제거
                d[k] = val
        return d

    def load_products(self, filters: dict | None = None):
        import locale
        locale.setlocale(locale.LC_ALL, '')  # 숫자 콤마 표시용

        if filters is None:                # ★ 추가
            filters = self._filters()

        self.products = self.data.get_products(filters)

        # ---------- 이미지 탭 ----------
        self.image_list.clear()
        for p in self.products:
            item = QListWidgetItem()
            pix = QPixmap(p.image_path) if p.image_path and Path(p.image_path).exists() else QPixmap()
            item.setIcon(QIcon(pix.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            item.setData(Qt.UserRole, p.id)

            # 즐겨찾기는 텍스트 앞에 ★ 표시
            label = f"{'★ ' if p.is_favorite else ''}{p.name}\n{p.karat} {p.weight_g}g"
            item.setText(label)
            item.setTextAlignment(Qt.AlignHCenter)

            self.image_list.addItem(item)

        # ---------- 목록 탭 ----------
        self.table.clear()
        headers = [
            "ID","이미지","품목","매입처","매입처상품번호","상품명","상품번호","함량","중량(g)","사이즈",
            "총QB수량","기/추","중/보 물림","중/보 공임","큐빅 공임","총공임","단종","재고",
            "즐겨찾기","수정"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.products))

        # Determine dynamic column indices for favorite and edit buttons
        fav_col = self.table.columnCount() - 2
        edit_col = self.table.columnCount() - 1

        for row, p in enumerate(self.products):
            category_map = {"E": "귀걸이", "R": "반지", "N": "목걸이", "B": "팔찌", "O": "기타"}
            category_kor = category_map.get(p.category, p.category)
            # ─── 0~14번 일반 데이터 셀 ───────────────
            base_vals = [
                p.id, "",                              # ID, 이미지
                category_kor,                          # 품목
                p.supplier_name,                       # 매입처
                p.supplier_item_no,                    # 매입처상품번호
                p.name,                                # 상품명
                p.product_code,                        # 상품번호
                p.karat,                               # 함량
                p.weight_g,                            # 중량(g)
                p.size,                                # 사이즈
                p.total_qb_qty,                        # 총QB수량 (now string, no formatting)
                _fmt_slash(p.basic_extra),      # ← 3000\n5000
                _fmt_slash(p.mid_back_bulim),
                _fmt_slash(p.mid_back_labor),
                p.cubic_labor,
                p.total_labor,
                "Y" if p.discontinued else "N",        # 단종
                p.stock_qty                            # 재고
            ]
            for col, val in enumerate(base_vals):
                item = QTableWidgetItem(str(val))
                if col == 0:
                    item.setData(Qt.UserRole, p.id)          # ID 저장
                self.table.setItem(row, col, item)

            # 이미지 셀: QLabel 위젯으로 추가하여 stretch 가능, 120x120 정사각형 셀 유지 (패딩)
            if p.image_path and Path(p.image_path).exists():
                # create a fixed-size square container
                size = self.CELL_HEIGHT
                lbl = QLabel()
                lbl.setFixedSize(size, size)
                lbl.setAlignment(Qt.AlignCenter)

                # load and scale pixmap to fit within the square, preserving aspect ratio
                pix = QPixmap(p.image_path)
                scaled = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl.setPixmap(scaled)

                # use a wrapper to center the label in its cell
                wrapper = self._make_centered_widget(lbl)
                self.table.setCellWidget(row, 1, wrapper)

            BTN_CSS = """
            QPushButton { border:none; background:transparent; }
            QPushButton:hover { background:#1890ff11; border-radius:4px; }
            """

            # Favorite button column
            star_btn = QPushButton()
            star_btn.setProperty("cellBtn", True)
            star_btn.setStyleSheet(BTN_CSS)
            star_btn.setIcon(self.STAR_ON if p.is_favorite else self.STAR_OFF)
            star_btn.setIconSize(QSize(24, 24))   # 아이콘 크기 = scaled 크기
            star_btn.setFixedSize(32, 32)
            star_btn.setFlat(True)                          # 테두리 없음
            star_btn.clicked.connect(partial(self._toggle_fav_cell, p.id))
            self.table.setCellWidget(row, fav_col, self._make_centered_widget(star_btn))

            # Edit button column
            edit_btn = QPushButton()
            edit_btn.setProperty("cellBtn", True)
            edit_btn.setStyleSheet(BTN_CSS)
            edit_btn.setIcon(self.EDIT_IC)
            edit_btn.setIconSize(QSize(24, 24))         # 아이콘 자체 크기
            edit_btn.setFixedSize(32, 32)               # 버튼 자체 크기
            edit_btn.setFlat(True)
            edit_btn.clicked.connect(partial(self._edit, pid_override=p.id))
            self.table.setCellWidget(row, edit_col, self._make_centered_widget(edit_btn))


        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self._apply_column_widths()

        # 이미지가 있는 행은 최소 IMG_SIDE 확보
        min_h = self.IMG_SIDE + 6
        for r in range(self.table.rowCount()):
            if self.table.rowHeight(r) < min_h:
                self.table.setRowHeight(r, min_h)

        self.table.setColumnHidden(0, True)


    def _show_popup(self,item):
        pid=item.data(Qt.UserRole); self._popup(pid)

    def _show_all(self):
        # 필터 UI 비우기
        for w in self.f_widgets.values():
            if isinstance(w, QComboBox):
                w.setCurrentIndex(0)
            else:
                w.clear()
        self.load_products({})   # 전체 조회

    def _show_favs(self):
        self.load_products({"is_favorite": "1"})

    def _table_click(self, row, col):
        pid = int(self.table.item(row, 0).data(Qt.UserRole))

        fav_col  = self.table.columnCount() - 2
        edit_col = self.table.columnCount() - 1

        if col == fav_col:          # ★
            self._toggle_fav_cell(pid)
        elif col == edit_col:       # ✎
            self._edit(pid_override=pid)

    def _row_dbl_clicked(self, item: QTableWidgetItem):
        """행 더블‑클릭 → 상세 팝업"""
        row = item.row()
        pid_item = self.table.item(row, 0)
        if pid_item:
            pid = int(pid_item.data(Qt.UserRole))
            self._popup(pid)


    def _popup(self, pid: int):
        p = self.data.get_product(pid)
        if not p:
            return
        dlg = DetailDialog(self, p)
        dlg.exec_()
    
    def _make_centered_widget(self, widget: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.addWidget(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return wrapper


    # CRUD
    def _add(self):
        d=ProductDialog(self); p=d.get_product()
        if p: self.data.add_product(p); self.load_products()
    def _edit(self, pid_override=None):
        pid = pid_override or self._current_id()
        if pid is None:
            QMessageBox.information(self, "알림", "수정할 상품 선택")
            return
        p = self.data.get_product(pid)
        dlg = ProductDialog(self, p)
        up = dlg.get_product()
        if up:
            up.id = pid
            # Prepare update data from the Product instance, excluding SQLAlchemy state and id
            data = {k: v for k, v in up.__dict__.items() if k not in ("_sa_instance_state", "id")}
            self.data.update_product(pid, **data)
            self.load_products()
    def _delete(self):
        pid=self._current_id()
        if pid is None: QMessageBox.information(self,"알림","삭제할 상품 선택"); return
        if QMessageBox.question(self,"확인","정말 삭제?")==QMessageBox.Yes:
            self.data.delete_product(pid); self.load_products()
    def _toggle_fav(self):
        pid = self._current_id()
        if pid is None:
            QMessageBox.information(self, "알림", "상품을 선택하세요.")
            return
    
        self.data.toggle_favorite(pid)
        self.load_products()

    def _toggle_fav_cell(self, pid: int):
        self.data.toggle_favorite(pid)
        self.load_products()          # 버튼·별 아이콘 새로고침

    def _current_id(self):
        if self.tabs.currentIndex()==0:
            it=self.image_list.currentItem(); return it.data(Qt.UserRole) if it else None
        else:
            row=self.table.currentRow(); return int(self.table.item(row,0).data(Qt.UserRole)) if row>=0 else None

def _set_light_palette(app: QApplication):
    from PyQt5.QtGui import QPalette, QColor
    pal = QPalette()
    pal.setColor(QPalette.Window,        QColor("#ffffff"))
    pal.setColor(QPalette.Base,          QColor("#ffffff"))
    pal.setColor(QPalette.AlternateBase, QColor("#fafafa"))
    pal.setColor(QPalette.Text,          QColor("#212121"))   # 거의 검정
    pal.setColor(QPalette.WindowText,    QColor("#212121"))
    pal.setColor(QPalette.ButtonText,    QColor("#212121"))
    pal.setColor(QPalette.Highlight,     QColor("#1890ff"))   # 포인트 블루
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)

def launch_app():
    app = QApplication(sys.argv)
    app.setStyle("fusion")          # 기본 Fusion 라이트
    _set_light_palette(app)         # 라이트 팔레트 설정

    app.setFont(QFont("맑은 고딕", 12))
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())