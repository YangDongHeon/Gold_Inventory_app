
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Product:
    id: Optional[int] = None
    # identification
    category: str = ""
    name: str = ""
    supplier_name: str = ""
    supplier_item_no: str = ""
    product_code: str = ""
    # specs
    karat: str = "14K"          # 14K / 18K / 24K
    weight_g: float = 0.0
    size: str = ""
    total_qb_qty: int = 0
    # cost
    labor_cost1: float = 0.0
    labor_cost2: float = 0.0
    # inventory
    set_no: str = ""
    discontinued: bool = False
    stock_qty: int = 0
    # media
    image_path: str = ""
    extra_images: List[str] = None
    notes: str = ""
    is_favorite: bool = False

    def dict_for_db(self):
        data = asdict(self)
        data["discontinued"] = int(self.discontinued)
        data["is_favorite"] = int(self.is_favorite)
        import json
        data["extra_images"] = json.dumps(self.extra_images or [])
        return data
