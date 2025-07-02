# config.py  (프로젝트 루트에 위치)
import sys
from pathlib import Path

def app_base_dir() -> Path:
    """
    • 개발 중  : 프로젝트 루트
    • PyInstaller exe : exe 가 있는 폴더
    """
    if getattr(sys, 'frozen', False):
        # exe 가 있는 폴더
        return Path(sys.executable).resolve().parent
    # config.py 가 있는 곳 == 프로젝트 루트
    return Path(__file__).resolve().parent.parent

def app_resource_path(*relative_parts) -> Path:
    """루트 기준 리소스 경로(Path 객체 반환)."""
    return app_base_dir().joinpath(*relative_parts)

# ── DB 설정 ────────────────────────────────────────────
DB_PATH  = app_resource_path('DB', 'gold_data.db') 
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # 폴더 자동 생성