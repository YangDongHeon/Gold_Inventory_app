
import sqlite3, json
from pathlib import Path
from typing import List, Optional, Dict
from .models import Product

class DataManager:
    def __init__(self, db_path: str | Path = "gold_data.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT NOT NULL,
                supplier_name TEXT,
                supplier_item_no TEXT,
                product_code TEXT,
                karat TEXT,
                weight_g REAL,
                size TEXT,
                total_qb_qty TEXT,
                labor_cost1 REAL,
                labor_cost2 REAL,
                set_no TEXT,
                discontinued INTEGER DEFAULT 0,
                stock_qty INTEGER,
                image_path TEXT,
                extra_images TEXT,
                notes TEXT,
                is_favorite INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def _row_to_product(self, row: sqlite3.Row | None) -> Product | None:
        if row is None:
            return None
        extra_images = json.loads(row["extra_images"] or "[]")
        return Product(
            id=row["id"],
            category=row["category"],
            name=row["name"],
            supplier_name=row["supplier_name"],
            supplier_item_no=row["supplier_item_no"],
            product_code=row["product_code"],
            karat=row["karat"],
            weight_g=row["weight_g"],
            size=row["size"],
            total_qb_qty=row["total_qb_qty"],
            labor_cost1=row["labor_cost1"],
            labor_cost2=row["labor_cost2"],
            set_no=row["set_no"],
            discontinued=bool(row["discontinued"]),
            stock_qty=row["stock_qty"],
            image_path=row["image_path"],
            extra_images=extra_images,
            notes=row["notes"],
            is_favorite=bool(row["is_favorite"]),
        )

    # CRUD
    def add_product(self, product: Product) -> int:
        with self.conn:
            cur = self.conn.execute(
                """INSERT INTO products
                (category,name,supplier_name,supplier_item_no,product_code,karat,weight_g,size,total_qb_qty,
                 labor_cost1,labor_cost2,set_no,discontinued,stock_qty,image_path,extra_images,notes,is_favorite)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    product.category,
                    product.name,
                    product.supplier_name,
                    product.supplier_item_no,
                    product.product_code,
                    product.karat,
                    product.weight_g,
                    product.size,
                    product.total_qb_qty,
                    product.labor_cost1,
                    product.labor_cost2,
                    product.set_no,
                    int(product.discontinued),
                    product.stock_qty,
                    product.image_path,
                    json.dumps(product.extra_images or []),
                    product.notes,
                    int(product.is_favorite),
                ),
            )
            return cur.lastrowid

    def update_product(self, product: Product):
        with self.conn:
            self.conn.execute(
                """UPDATE products SET
                category=?,name=?,supplier_name=?,supplier_item_no=?,product_code=?,karat=?,weight_g=?,size=?,total_qb_qty=?,
                labor_cost1=?,labor_cost2=?,set_no=?,discontinued=?,stock_qty=?,image_path=?,extra_images=?,notes=?,is_favorite=?
                WHERE id=?""",
                (
                    product.category,
                    product.name,
                    product.supplier_name,
                    product.supplier_item_no,
                    product.product_code,
                    product.karat,
                    product.weight_g,
                    product.size,
                    product.total_qb_qty,
                    product.labor_cost1,
                    product.labor_cost2,
                    product.set_no,
                    int(product.discontinued),
                    product.stock_qty,
                    product.image_path,
                    json.dumps(product.extra_images or []),
                    product.notes,
                    int(product.is_favorite),
                    product.id,
                ),
            )

    def delete_product(self, product_id: int):
        with self.conn:
            self.conn.execute("DELETE FROM products WHERE id=?", (product_id,))

    def get_product(self, product_id: int) -> Product | None:
        row = self.conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        return self._row_to_product(row)

    def search_products(self, filters: Dict[str, str] | None = None,
                        any_text: str = "") -> List[Product]:
        """
        filters  : 개별 필드 검색   {"name":"루비", "supplier_name":"A공장"}
        any_text : 모든 주요 컬럼을 한꺼번에 OR 검색
        """
        filters = filters or {}
        column_map = {
            "category": "category",
            "name": "name",
            "supplier_name": "supplier_name",
            "supplier_item_no": "supplier_item_no",
            "product_code": "product_code",
            "set_no": "set_no",
            "karat": "karat",
            "discontinued": "discontinued",
            "is_favorite": "is_favorite"
        }

        clauses, params = [], []

        # 개별 필터
        for ui_key, val in filters.items():
            val = (val or "").strip()
            if not val:
                continue
            col = column_map.get(ui_key)
            if not col:
                continue

            if col == "discontinued":
                clauses.append("discontinued = ?")
                params.append(1 if val.upper() in ("Y", "TRUE", "1") else 0)
            elif col == "is_favorite":            # ★ 추가: 즐겨찾기 필터
                clauses.append("is_favorite = ?")
                params.append(1 if val in ("1", "True", "true", "Y") else 0)
            elif col in ("stock_qty", "total_qb_qty", "weight_g",
                         "labor_cost1", "labor_cost2"):
                # 숫자 필드는 정확 매칭
                clauses.append(f"{col} = ?")
                params.append(val)
            else:
                # 문자열 → LIKE, 대소문자 구분 안 함
                clauses.append(f"{col} LIKE ? COLLATE NOCASE")
                params.append(f"%{val}%")

        # any_text가 있으면 주요 컬럼 OR 검색
        if any_text.strip():
            cols = ("name", "supplier_name", "product_code",
                    "supplier_item_no", "category")
            or_clause = " OR ".join(f"{c} LIKE ? COLLATE NOCASE" for c in cols)
            clauses.append(f"({or_clause})")
            params.extend([f"%{any_text.strip()}%"] * len(cols))

        # 쿼리 조립
        sql = "SELECT * FROM products"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY is_favorite DESC, id DESC"

        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_product(r) for r in rows]

    def toggle_favorite(self, product_id: int):
        with self.conn:
            self.conn.execute("UPDATE products SET is_favorite = NOT is_favorite WHERE id=?", (product_id,))
