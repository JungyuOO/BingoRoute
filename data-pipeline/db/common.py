"""데이터 파이프라인에서 재사용하는 DB 접속 유틸리티."""

import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

# 개발 환경에서는 .env를 사용할 수 있지만, 컨테이너 주입 값이 있으면 그대로 쓴다.
load_dotenv(find_dotenv(), override=False)


def _resolve_env(*names: str, default: str | None = None) -> str | None:
    """주어진 환경 변수 이름 목록에서 먼저 발견되는 값을 반환한다."""
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


CFG_RAW = {
    "host": _resolve_env("DB_HOST", "DATABASE_HOST", default="localhost"),
    "port": _resolve_env("DB_PORT", "DATABASE_PORT", default="5432"),
    "user": _resolve_env("DB_USER", "DATABASE_USER"),
    "password": _resolve_env("DB_PASSWORD", "DATABASE_PASSWORD"),
    "db": _resolve_env("DB_NAME", "DATABASE_NAME"),
}

missing = [label for label, value in CFG_RAW.items() if value in (None, "")]
if missing:
    raise RuntimeError(f"환경변수 누락: {', '.join(missing)}")

CFG = {
    **CFG_RAW,
    "port": int(CFG_RAW["port"]),
}


def ensure_tables(_ddls=None) -> None:
    """
    테이블 생성은 docker/init.sql에서 처리되므로 더 이상 수행하지 않는다.
    기존 코드 호환을 위해 자리만 유지한다.
    """
    return None


def pg_connect():
    """현재 환경변수 설정을 이용해 psycopg2 커넥션을 생성한다."""
    return psycopg2.connect(
        host=CFG["host"],
        port=CFG["port"],
        user=CFG["user"],
        password=CFG["password"],
        dbname=CFG["db"],
    )
