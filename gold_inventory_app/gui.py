import sys, json
from pathlib import Path
from typing import Dict
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont
# from PyQt5.QtWidgets ... (unchanged)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCheckBox, QSizePolicy, QAbstractSpinBox
)
# Additional imports for DetailDialog
from .models import Product
from PyQt5.QtWidgets import QDialog, QFormLayout
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
            ("품목", product.category),
            ("함량", product.karat),
            ("중량", f"{product.weight_g} g"),
            ("공임", f"₩{product.labor_cost1:,.0f} / ₩{product.labor_cost2:,.0f}"),
            ("사이즈", product.size),
            ("QB합계", product.total_qb_qty),
            ("세트번호", product.set_no),
            ("단종", "Y" if product.discontinued else "N"),
            ("재고", product.stock_qty),
            ("매입처", f"{product.supplier_name} ({product.supplier_item_no})"),
            ("상품코드", product.product_code),
            ("비고", product.notes or "-"),
        ]
        for key, val in fields:
            lbl_key = QLabel(f"{key}:")
            lbl_key.setFont(font_bold)
            lbl_val = QLabel(str(val))
            form.addRow(lbl_key, lbl_val)
        main_layout.addLayout(form)
        # ─── Bottom: OK Button ────────────────
        btn_ok = QPushButton("닫기")
        btn_ok.clicked.connect(self.accept)
        main_layout.addWidget(btn_ok, alignment=Qt.AlignBottom)
# Ensure QApplication is imported for combo box style setting
from PyQt5.QtWidgets import QApplication
from .db import DataManager
from .models import Product
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

        self.labor1_spin = QDoubleSpinBox(); self.labor1_spin.setMaximum(1_000_000_000); self.labor1_spin.setPrefix("₩ ")
        self.labor2_spin = QDoubleSpinBox(); self.labor2_spin.setMaximum(1_000_000_000); self.labor2_spin.setPrefix("₩ ")

        self.set_no_edit = QLineEdit()
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
        layout.addRow("기본공임1", self.labor1_spin)
        layout.addRow("물림(추가공임)", self.labor2_spin)
        layout.addRow("세트번호", self.set_no_edit)
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
        self.labor1_spin.setValue(p.labor_cost1)
        self.labor2_spin.setValue(p.labor_cost2)
        self.set_no_edit.setText(p.set_no)
        self.discontinued_cb.setCurrentText("Y" if p.discontinued else "N")
        self.stock_spin.setValue(p.stock_qty)
        self.img_path_edit.setText(p.image_path)
        self.notes_edit.setPlainText(p.notes)
        self.favorite_chk.setChecked(p.is_favorite)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.img_path_edit.setText(path)

    def get_product(self) -> Product | None:
        if self.exec_() != QDialog.Accepted: return None
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "오류", "상품명을 입력하세요."); return None
        
        cat_txt  = self.category_cb.currentText()
        category = cat_txt.split()[0] if cat_txt else ""

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
            labor_cost1=self.labor1_spin.value(),
            labor_cost2=self.labor2_spin.value(),
            set_no=self.set_no_edit.text().strip(),
            discontinued=self.discontinued_cb.currentText()=="Y",
            stock_qty=self.stock_spin.value(),
            image_path=self.img_path_edit.text().strip(),
            extra_images=[],
            notes=self.notes_edit.toPlainText(),
            is_favorite=self.favorite_chk.isChecked()
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_icons()
        self.setWindowTitle("GOLD MANAGER")
        self.resize(1200,700)
        self.data = DataManager()
        self.IMAGE_MAX = 200  # max width/height for image cells
        self._build_ui()
        self.load_products()

    def _init_icons(self):
        from PyQt5.QtCore import Qt
        icon_dir = Path(__file__).parent / "icons"

        def _scaled_icon(path: Path, size: int = 24) -> QIcon:
            pm = QPixmap(str(path)).scaled(
                size, size,  Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            return QIcon(pm)

        self.STAR_ON  = _scaled_icon(icon_dir / "star_on.png")
        self.STAR_OFF = _scaled_icon(icon_dir / "star_off.png")
        self.EDIT_IC  = _scaled_icon(icon_dir / "pencil.png")

    def _apply_column_widths(self):
        """고정 폭 열(이미지/버튼) 재지정 + 상품명 열 스트레치"""
        hdr = self.table.horizontalHeader()
        image_col = 1
        fav_col = self.table.columnCount() - 2
        edit_col = self.table.columnCount() - 1
        for col, w in (
            (image_col, 140),
            (fav_col, 80),
            (edit_col, 40)
        ):
            hdr.setSectionResizeMode(col, QHeaderView.Fixed)
            self.table.setColumnWidth(col, w)
        # Do not stretch the last (수정) column; instead let the 이미지 column expand
        hdr.setStretchLastSection(False)
        # 이미지 column (index 1) takes all extra horizontal space
        hdr.setSectionResizeMode(image_col, QHeaderView.Stretch)

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
        set_edit = QLineEdit(); set_edit.setPlaceholderText("세트번호"); self.f_widgets["set_no"]=set_edit; search_h.addWidget(set_edit)
        
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
        self.image_list.setIconSize(QSize(200,200))
        self.image_list.setSpacing(15)
        self.image_list.itemClicked.connect(self._show_popup)
        self.tabs.addTab(self.image_list, "이미지")

        self.table = QTableWidget()
        # Dynamically set column count and headers
        headers = [
            "ID","이미지","품목","매입처","매입처상품번호","상품번호","함량","중량(g)","사이즈",
            "총QB수량","기본공임","물림(추가공임)","세트번호","단종","재고",
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
        IMAGE_CELL_HEIGHT = 200
        ROW_PADDING = 10
        self.table.verticalHeader().setDefaultSectionSize(IMAGE_CELL_HEIGHT + ROW_PADDING)
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

        self.products = self.data.search_products(filters)

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
            "ID","이미지","품목","매입처","매입처상품번호","상품번호","함량","중량(g)","사이즈",
            "총QB수량","기본공임","물림(추가공임)","세트번호","단종","재고",
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
                p.product_code,                        # 상품번호
                p.karat,                               # 함량
                p.weight_g,                            # 중량(g)
                p.size,                                # 사이즈
                p.total_qb_qty,                        # 총QB수량 (now string, no formatting)
                locale.format_string("%d", p.labor_cost1, grouping=True),  # 기본공임1
                locale.format_string("%d", p.labor_cost2, grouping=True),  # 물림(추가공임)
                p.set_no,                              # 세트번호
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
                size = 200
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
        self._apply_column_widths()
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
        # 단건 클릭에서는 즐겨찾기 / 수정 버튼만 처리
        pid = int(self.table.item(row,0).data(Qt.UserRole))
        if col == 16:      # ★ 버튼
            self._toggle_fav_cell(pid)
        elif col == 17:    # ✎ 버튼
            self._edit(pid_override=pid)
        # 그 외는 선택만 하고 아무 동작 안 함

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
    def _edit(self,pid_override=None):
        pid=pid_override or self._current_id()
        if pid is None: QMessageBox.information(self,"알림","수정할 상품 선택"); return
        p=self.data.get_product(pid); dlg=ProductDialog(self,p); up=dlg.get_product()
        if up: up.id=pid; self.data.update_product(up); self.load_products()
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

    app.setFont(QFont("맑은 고딕", 14))
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())