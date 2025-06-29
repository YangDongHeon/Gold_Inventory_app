import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
DB_PATH = Path(os.getenv('DB_PATH', PROJECT_ROOT / 'DB' / 'gold_data.db'))
