import sys
from pathlib import Path
from typing import Dict
from functools import partial
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QDialog, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCheckBox, QSizePolicy, QAbstractSpinBox,
    QDateEdit, QGridLayout, QFormLayout, QGroupBox
)

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from db import DataManager
from models import Product
from config import app_resource_path
from .product_dialog import ProductDialog
from .sales_record_dialog import SalesRecordDialog, SalesRecordDetailDialog
from .detail_dialog import DetailDialog

def _fmt_slash(val: str) -> str:
    return val.replace("/", "\n") if val else val

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
        self.load_sales()

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

        # --- 이미지 탭 search bar ---
        search_h_img = QHBoxLayout()
        self.f_widgets_img: Dict[str, QLineEdit|QComboBox] = {}
        cat_cb_img = QComboBox(); cat_cb_img.addItems(["","E","R","N","B","O"])
        cat_cb_img.setEditable(True)
        cat_cb_img.lineEdit().setReadOnly(True)
        cat_cb_img.lineEdit().setPlaceholderText("품목")
        cat_cb_img.setFixedWidth(80)
        cat_cb_img.setToolTip("품목 필터")
        self.f_widgets_img["category"]=cat_cb_img; search_h_img.addWidget(cat_cb_img)

        sup_edit_img = QLineEdit(); sup_edit_img.setPlaceholderText("매입처명"); self.f_widgets_img["supplier_name"]=sup_edit_img; search_h_img.addWidget(sup_edit_img)
        sup_no_img = QLineEdit(); sup_no_img.setPlaceholderText("매입처상품번호"); self.f_widgets_img["supplier_item_no"]=sup_no_img; search_h_img.addWidget(sup_no_img)
        name_edit_img = QLineEdit(); name_edit_img.setPlaceholderText("상품명"); self.f_widgets_img["name"]=name_edit_img; search_h_img.addWidget(name_edit_img)
        code_edit_img = QLineEdit(); code_edit_img.setPlaceholderText("상품번호"); self.f_widgets_img["product_code"]=code_edit_img; search_h_img.addWidget(code_edit_img)

        disc_cb_img = QComboBox(); disc_cb_img.addItems(["","Y","N"])
        disc_cb_img.setEditable(True)
        disc_cb_img.lineEdit().setReadOnly(True)
        disc_cb_img.lineEdit().setPlaceholderText("단종")
        disc_cb_img.setFixedWidth(80)
        disc_cb_img.setToolTip("단종")
        self.f_widgets_img["discontinued"]=disc_cb_img; search_h_img.addWidget(disc_cb_img)

        search_btn_img = QPushButton("검색"); search_btn_img.clicked.connect(lambda: self.load_products(self._filters())); search_h_img.addWidget(search_btn_img)
        reset_btn_img = QPushButton("메인으로"); reset_btn_img.clicked.connect(self._show_all); search_h_img.addWidget(reset_btn_img)

        product_search_widget_img = QWidget()
        product_search_widget_img.setLayout(search_h_img)

        # --- 목록 탭 search bar ---
        search_h_list = QHBoxLayout()
        self.f_widgets_list: Dict[str, QLineEdit|QComboBox] = {}
        cat_cb_list = QComboBox(); cat_cb_list.addItems(["","E","R","N","B","O"])
        cat_cb_list.setEditable(True)
        cat_cb_list.lineEdit().setReadOnly(True)
        cat_cb_list.lineEdit().setPlaceholderText("품목")
        cat_cb_list.setFixedWidth(80)
        cat_cb_list.setToolTip("품목 필터")
        self.f_widgets_list["category"]=cat_cb_list; search_h_list.addWidget(cat_cb_list)

        sup_edit_list = QLineEdit(); sup_edit_list.setPlaceholderText("매입처명"); self.f_widgets_list["supplier_name"]=sup_edit_list; search_h_list.addWidget(sup_edit_list)
        sup_no_list = QLineEdit(); sup_no_list.setPlaceholderText("매입처상품번호"); self.f_widgets_list["supplier_item_no"]=sup_no_list; search_h_list.addWidget(sup_no_list)
        name_edit_list = QLineEdit(); name_edit_list.setPlaceholderText("상품명"); self.f_widgets_list["name"]=name_edit_list; search_h_list.addWidget(name_edit_list)
        code_edit_list = QLineEdit(); code_edit_list.setPlaceholderText("상품번호"); self.f_widgets_list["product_code"]=code_edit_list; search_h_list.addWidget(code_edit_list)

        disc_cb_list = QComboBox(); disc_cb_list.addItems(["","Y","N"])
        disc_cb_list.setEditable(True)
        disc_cb_list.lineEdit().setReadOnly(True)
        disc_cb_list.lineEdit().setPlaceholderText("단종")
        disc_cb_list.setFixedWidth(80)
        disc_cb_list.setToolTip("단종")
        self.f_widgets_list["discontinued"]=disc_cb_list; search_h_list.addWidget(disc_cb_list)

        search_btn_list = QPushButton("검색"); search_btn_list.clicked.connect(lambda: self.load_products(self._filters())); search_h_list.addWidget(search_btn_list)
        reset_btn_list = QPushButton("메인으로"); reset_btn_list.clicked.connect(self._show_all); search_h_list.addWidget(reset_btn_list)

        product_search_widget_list = QWidget()
        product_search_widget_list.setLayout(search_h_list)

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

        /* keep line
edit and spin
box text aligned */
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
        /* 

disabled 색상을 파란계열로 유지 */
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

        # --- 이미지 탭: wrap image list in a tab, insert search widget at top
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        # Insert search widget at the top
        image_layout.insertWidget(0, product_search_widget_img)
        self.image_list = QListWidget()
        self.image_list.setFlow(QListWidget.LeftToRight)
        self.image_list.setResizeMode(QListWidget.Adjust)   # ← ★ 중요: 크기 변경 시 재배치
        self.image_list.setWrapping(True)                   # ← 행이 가득 차면 자동 줄바꿈
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(self.IMAGE_SIZE,self.IMAGE_SIZE))
        self.image_list.setSpacing(15)
        self.image_list.itemDoubleClicked.connect(self._show_popup)
        image_layout.addWidget(self.image_list)
        self.tabs.addTab(image_tab, "이미지")

        # --- 목록 탭: wrap table in a tab, insert search widget at top
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)
        # Insert search widget at the top
        list_layout.insertWidget(0, product_search_widget_list)
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
        list_layout.addWidget(self.table)
        self.tabs.addTab(list_tab, "목록")

        # Sales Tab
        sales_widget = QWidget()
        sales_layout = QVBoxLayout(sales_widget)

        sales_search_layout = QHBoxLayout()
        self.sales_start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.sales_start_date.setCalendarPopup(True)
        self.sales_end_date = QDateEdit(QDate.currentDate())
        self.sales_end_date.setCalendarPopup(True)
        self.sales_customer_name = QLineEdit()
        self.sales_customer_name.setPlaceholderText("고객명")
        self.sales_product_name = QLineEdit()
        self.sales_product_name.setPlaceholderText("제품명")
        sales_search_btn = QPushButton("검색")
        sales_search_btn.clicked.connect(self.load_sales)
        sales_reset_btn = QPushButton("메인으로")
        sales_reset_btn.clicked.connect(self._show_all_sales)

        sales_search_layout.addWidget(QLabel("판매일자:"))
        sales_search_layout.addWidget(self.sales_start_date)
        sales_search_layout.addWidget(QLabel("~"))
        sales_search_layout.addWidget(self.sales_end_date)
        sales_search_layout.addWidget(self.sales_customer_name)
        sales_search_layout.addWidget(self.sales_product_name)
        sales_search_layout.addWidget(sales_search_btn)
        sales_search_layout.addWidget(sales_reset_btn)
        sales_layout.addLayout(sales_search_layout)

        self.sales_table = QTableWidget()
        self.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        sales_layout.addWidget(self.sales_table)
        self.sales_table.itemDoubleClicked.connect(self._row_dbl_clicked_sales)
        self.tabs.addTab(sales_widget, "판매관리")

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
        # Use correct filter widgets dict depending on current tab
        tab = self.tabs.currentIndex()
        if tab == 0:
            widgets = self.f_widgets_img
        elif tab == 1:
            widgets = self.f_widgets_list
        else:
            widgets = {}
        d = {}
        for k, w in widgets.items():
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

    def load_sales(self):
        filters = {
            'start_date': self.sales_start_date.date().toPyDate(),
            'end_date': self.sales_end_date.date().toPyDate(),
            'customer_name': self.sales_customer_name.text().strip(),
            'product_name': self.sales_product_name.text().strip(),
        }
        sales_records = self.data.get_sales_records(filters)
        self.sales_table.setRowCount(len(sales_records))
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["날짜", "고객명", "상품명", "판매가", "수정"])

        BTN_CSS = """
        QPushButton { border:none; background:transparent; }
        QPushButton:hover { background:#1890ff11; border-radius:4px; }
        """

        for row, record in enumerate(sales_records):
            # Store the record ID in the UserRole of the date cell
            item_date = QTableWidgetItem(str(record.sale_date))
            item_date.setData(Qt.UserRole, record.id)
            self.sales_table.setItem(row, 0, item_date)
            self.sales_table.setItem(row, 1, QTableWidgetItem(record.customer_name))
            self.sales_table.setItem(row, 2, QTableWidgetItem(record.product_name))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"{record.final_sale_price:,} 원"))

            edit_btn = QPushButton()
            edit_btn.setProperty("cellBtn", True)
            edit_btn.setStyleSheet(BTN_CSS)
            edit_btn.setIcon(self.EDIT_IC)
            edit_btn.setIconSize(QSize(24, 24))
            edit_btn.setFixedSize(32, 32)
            edit_btn.setFlat(True)
            edit_btn.clicked.connect(partial(self._edit_sales_record, record.id))
            self.sales_table.setCellWidget(row, 4, self._make_centered_widget(edit_btn))

        # Set column resize modes as specified
        header = self.sales_table.horizontalHeader()
        # "수정" column (index 4): Fixed width
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.sales_table.setColumnWidth(4, 50)
        # "상품명" (index 2) and "판매가" (index 3): Stretch
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        # Remaining columns: ResizeToContents
        for idx in range(self.sales_table.columnCount()):
            if idx not in (2, 3, 4):
                header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
        # Prevent last section from stretching
        header.setStretchLastSection(False)


    def _show_popup(self,item):
        pid=item.data(Qt.UserRole); self._popup(pid)

    def _show_all(self):
        # 필터 UI 비우기 - use correct widgets dict for tab
        tab = self.tabs.currentIndex()
        if tab == 0:
            widgets = self.f_widgets_img
        elif tab == 1:
            widgets = self.f_widgets_list
        else:
            widgets = {}
        for w in widgets.values():
            if isinstance(w, QComboBox):
                w.setCurrentIndex(0)
            else:
                w.clear()
        self.load_products({})   # 전체 조회

    def _show_all_sales(self):
        """판매관리(판매기록) 검색바의 필터를 초기화하고 전체 판매기록을 다시 로드합니다."""
        self.sales_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.sales_end_date.setDate(QDate.currentDate())
        self.sales_customer_name.clear()
        self.sales_product_name.clear()
        self.load_sales()

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
        """행 더블
클릭 → 상세 팝업"""
        row = item.row()
        pid_item = self.table.item(row, 0)
        if pid_item:
            pid = int(pid_item.data(Qt.UserRole))
            self._popup(pid)


    def _row_dbl_clicked_sales(self, item: QTableWidgetItem):
        """판매 기록 행 더블
클릭 → 상세 팝업"""
        row = item.row()
        record_id = self.sales_table.item(row, 0).data(Qt.UserRole)
        record = self.data.get_sales_record(record_id)
        if record:
            dlg = SalesRecordDetailDialog(self, record)
            dlg.exec_()

    def _edit_sales_record(self, record_id: int):
        record = self.data.get_sales_record(record_id)
        if not record:
            QMessageBox.warning(self, "오류", "판매 기록을 찾을 수 없습니다.")
            return
        
        dlg = SalesRecordDialog(self, record)
        updated_record = dlg.get_sales_record_data()
        if updated_record:
            data = {k: v for k, v in updated_record.__dict__.items() if k != "id" and not k.startswith('_sa_')}
            self.data.update_sales_record(record_id, **data)
            QMessageBox.information(self, "성공", "판매 기록이 업데이트되었습니다.")
            self.load_sales()

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
