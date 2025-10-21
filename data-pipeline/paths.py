"""데이터 파이프라인에서 공통으로 사용하는 경로 상수 모음."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_DATA_DIR = DATA_DIR / "db_data"
ENV_FILE = BASE_DIR / ".env"


def ensure_data_dirs() -> None:
    """원천(raw)·전처리 결과 디렉터리가 없으면 생성한다."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DB_DATA_DIR.mkdir(parents=True, exist_ok=True)
