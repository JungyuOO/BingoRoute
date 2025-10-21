"""코드 테이블 관련 전처리 결과를 PostgreSQL에 증분 적재한다."""

from typing import Optional

import os
import sys

import pandas as pd
from psycopg2.extras import execute_batch, execute_values

from db.common import pg_connect

# 상대 경로 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# code_table: SYS/ADD 루트를 포함한 전체 분류/지역 코드 저장 테이블 (PostgreSQL 버전)
DDL_CODE_TABLE = """
CREATE TABLE IF NOT EXISTS code_table (
  code VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  upper_code VARCHAR(20) NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_code_table_self FOREIGN KEY (upper_code)
    REFERENCES code_table(code)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
"""

# 상위 코드 검색을 빠르게 하기 위한 인덱스 (PostgreSQL에서 별도 생성 필요)
DDL_CODE_TABLE_INDEX = """
CREATE INDEX IF NOT EXISTS ix_code_table_upper ON code_table (upper_code);
"""


def _now() -> pd.Timestamp:
    # 감사 컬럼을 채우실 때 사용할 서울 시간 타임스탬프를 제공합니다.

    return pd.Timestamp.now(tz="Asia/Seoul").tz_localize(None)


def _ensure_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    # created_at과 updated_at 컬럼의 누락값을 현재 시각으로 보정해 드립니다.

    now = _now()
    for col in ("created_at", "updated_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT
        df[col] = df[col].fillna(now)
    return df


def _split_new_changed(
    df: pd.DataFrame,
    existing: pd.DataFrame,
    key: str,
    compare_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # 증분 적재 시 신규 건과 변경 건을 구분해 드립니다.

    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), existing.set_index(key)

    incoming = df.set_index(key)
    existing_indexed = existing.set_index(key)
    new_idx = incoming.index.difference(existing_indexed.index)
    new_df = incoming.loc[new_idx].reset_index()

    overlap_idx = incoming.index.intersection(existing_indexed.index)
    if overlap_idx.empty:
        return new_df, pd.DataFrame(), existing_indexed

    diff_mask = pd.Series(False, index=overlap_idx)
    for col in compare_cols:
        exist_col = existing_indexed.loc[overlap_idx, col]
        inc_col = incoming.loc[overlap_idx, col]
        equal = exist_col.eq(inc_col) | (exist_col.isna() & inc_col.isna())
        diff_mask |= ~equal

    changed_idx = diff_mask[diff_mask].index
    changed_df = incoming.loc[changed_idx].reset_index()
    return new_df, changed_df, existing_indexed


def _normalize_code_table(df: pd.DataFrame) -> pd.DataFrame:
    # 문자열을 정리하고 필수 컬럼을 검증해 드립니다.

    missing = {"code", "name", "upper_code"} - set(df.columns)
    if missing:
        raise ValueError(f"code_table DataFrame에 누락된 컬럼: {sorted(missing)}")

    cleaned = df.copy()
    if cleaned["code"].isna().any():
        raise ValueError("code 컬럼에 NULL이 있습니다")
    if cleaned["name"].isna().any():
        raise ValueError("name 컬럼에 NULL이 있습니다")

    cleaned["code"] = cleaned["code"].astype(str).str.strip()
    cleaned["name"] = cleaned["name"].astype(str).str.strip()
    cleaned["upper_code"] = cleaned["upper_code"].apply(
        lambda v: None if pd.isna(v) or str(v).strip() == "" else str(v).strip()
    )

    if (cleaned["code"] == "").any():
        raise ValueError("code 컬럼에 빈 문자열이 있습니다")

    if cleaned["code"].duplicated().any():
        duplicates = cleaned.loc[cleaned["code"].duplicated(), "code"].unique()
        raise ValueError(f"중복 code 값 발견: {duplicates.tolist()}")

    return cleaned


def _sort_by_hierarchy(df: pd.DataFrame) -> pd.DataFrame:
    # 부모 코드가 항상 자식보다 먼저 오도록 정렬해 드립니다.

    if df.empty:
        return df

    lookup = df.set_index("code")["upper_code"].to_dict()
    levels: dict[str, int] = {}

    def resolve(code: str, trail: Optional[set[str]] = None) -> int:
        if code in levels:
            return levels[code]
        trail = trail or set()
        if code in trail:
            return 0
        trail.add(code)
        parent = lookup.get(code)
        if not parent:
            level = 0
        else:
            level = resolve(parent, trail) + 1
        trail.remove(code)
        levels[code] = level
        return level

    # 동일 레벨에서는 기존 순서를 유지해 ADD 블록/시군구 묶음이 깨지지 않도록.
    ordered = df.assign(
        _level=df["code"].map(resolve),
        _order=pd.RangeIndex(len(df)),
    )
    ordered = ordered.sort_values(["_level", "_order"]).drop(columns=["_level", "_order"])
    return ordered.reset_index(drop=True)


def _to_python(value):
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if pd.isna(value):
        return None
    return value


def _prepare_records(df: pd.DataFrame, columns: list[str]) -> list[tuple]:
    return [tuple(_to_python(v) for v in row) for row in df[columns].itertuples(index=False, name=None)]


def ingest_code_table(df: Optional[pd.DataFrame]) -> None:
    # 전처리 결과를 code_table에 증분으로 적재해 드립니다.

    if df is None or df.empty:
        return

    df = _normalize_code_table(df)
    df = _ensure_timestamps(df)
    df = _sort_by_hierarchy(df)

    with pg_connect() as conn:
        existing = pd.read_sql(
            "SELECT code, name, upper_code, created_at, updated_at FROM code_table",
            conn,
        )

        new_df, changed_df, existing_indexed = _split_new_changed(
            df,
            existing,
            key="code",
            compare_cols=["name", "upper_code"],
        )

        insert_cols = ["code", "name", "upper_code", "created_at", "updated_at"]

        if not new_df.empty:
            new_df = _ensure_timestamps(_sort_by_hierarchy(new_df))
            records = _prepare_records(new_df, insert_cols)
            if records:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        INSERT INTO code_table (code, name, upper_code, created_at, updated_at)
                        VALUES %s
                        ON CONFLICT (code) DO NOTHING
                        """,
                        records,
                        page_size=1000,
                    )
                print(f"[OK] code_table 신규 {len(records):,}건")

        if not changed_df.empty:
            now = _now()
            changed_df["updated_at"] = now
            changed_df["created_at"] = existing_indexed.loc[changed_df["code"], "created_at"].values

            params = [
                (
                    _to_python(row.name),
                    _to_python(row.upper_code),
                    _to_python(row.updated_at),
                    row.code,
                )
                for row in changed_df.itertuples(index=False)
            ]
            if params:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        UPDATE code_table
                           SET name = %s,
                               upper_code = %s,
                               updated_at = %s
                         WHERE code = %s
                        """,
                        params,
                        page_size=1000,
                    )
                print(f"[OK] code_table 갱신 {len(params):,}건")


def ensure_tables_created() -> None:
    """테이블 생성은 docker/init.sql에서 처리되므로 이 함수는 더 이상 작업하지 않습니다."""
    return


def main(
    code_df: Optional[pd.DataFrame] = None,
    *,
    write_to_disk: bool = False,
) -> None:
    """필요 시 전처리부터 수행한 뒤 code_table에 데이터를 반영한다."""

    print("⭐")
    from preprocess import base as preprocess_base

    ensure_tables_created()

    if code_df is None:
        code_df = preprocess_base.main(write_to_disk=write_to_disk)

    ingest_code_table(code_df)


if __name__ == "__main__":
    main()
