"""관광지 전처리 결과를 PostgreSQL에 적재하는 헬퍼 함수들."""

from __future__ import annotations

from typing import Optional
from pathlib import Path
import os
import sys

import pandas as pd
import numpy as np
from psycopg2.extras import execute_batch, execute_values

from db.common import pg_connect
from paths import RAW_DIR

DDL_TOUR_SPOT = """
CREATE TABLE IF NOT EXISTS tourist_spot (
    content_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    firstimage VARCHAR(500),
    firstimage2 VARCHAR(500),
    category_code VARCHAR(20),
    category_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cat_code FOREIGN KEY (category_code) REFERENCES code_table(code)
        ON UPDATE CASCADE ON DELETE SET NULL
);
"""

DDL_TOUR_DETAIL = """
CREATE TABLE IF NOT EXISTS tourist_spot_detail (
    id BIGSERIAL PRIMARY KEY,
    content_id VARCHAR(20) NOT NULL,
    address_code VARCHAR(20),
    sigungu_name VARCHAR(100),
    zip_code VARCHAR(20),
    address VARCHAR(200),
    map_x NUMERIC(11, 6),
    map_y NUMERIC(11, 6),
    intro_serial_num INT,
    content_type_id VARCHAR(10),
    tel VARCHAR(50),
    restdate TEXT,
    useseason TEXT,
    usetime TEXT,
    is_parking SMALLINT,
    is_baby_carriage SMALLINT,
    is_pet SMALLINT,
    is_credit_card SMALLINT,
    info_serial_num VARCHAR(50),
    info_name VARCHAR(200),
    info_text TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_content_intro_info UNIQUE (content_id, intro_serial_num, info_serial_num),
    CONSTRAINT fk_detail_sigungu FOREIGN KEY (address_code) REFERENCES code_table(code)
        ON UPDATE CASCADE ON DELETE SET NULL
);
"""

DDL_SET = (DDL_TOUR_SPOT, DDL_TOUR_DETAIL)

# 상대 경로 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


def ensure_tour_tables() -> None:
    """테이블 생성은 docker/init.sql에서 처리되므로 더 이상 아무 것도 하지 않습니다."""
    return


def _load_code_table() -> pd.DataFrame:
    with pg_connect() as conn:
        try:
            return pd.read_sql("SELECT code, name, upper_code FROM code_table", conn)
        except Exception:
            return pd.DataFrame(columns=["code", "name", "upper_code"])


def _ensure_datetime(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def _to_python(value):
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    if hasattr(value, 'item') and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except Exception:
            pass
    return value


def ingest_tour_spot(
    df: Optional[pd.DataFrame],
    code_df: Optional[pd.DataFrame],
) -> None:
    if df is None or df.empty:
        return

    ensure_tour_tables()

    work = df.copy()
    if "content_id" not in work.columns:
        raise ValueError("tour_spot dataframe must contain content_id column")

    if code_df is not None and not code_df.empty and "category_code" in work.columns:
        lookup = code_df[["code", "name"]].rename(
            columns={"code": "category_code", "name": "category_name"}
        )
        work = work.merge(lookup, on="category_code", how="left")
    else:
        work["category_name"] = None

    for col in ["content_id", "title", "firstimage", "firstimage2", "category_code", "category_name"]:
        if col in work.columns:
            work[col] = work[col].astype(str).str.strip()
            work[col] = work[col].replace({"": None})

    work = _ensure_datetime(work, ["created_at", "updated_at"])

    with pg_connect() as conn:
        existing = pd.read_sql(
            "SELECT content_id, title, firstimage, firstimage2, category_code, category_name, created_at, updated_at FROM tourist_spot",
            conn,
        )

        work = work.drop_duplicates(subset=["content_id"]).set_index("content_id")
        existing = existing.drop_duplicates(subset=["content_id"]).set_index("content_id")

        new_idx = work.index.difference(existing.index)
        new_rows = work.loc[new_idx].reset_index()

        overlap_idx = work.index.intersection(existing.index)
        changed_mask = pd.Series(False, index=overlap_idx)
        compare_cols = ["title", "firstimage", "firstimage2", "category_code", "category_name"]
        for col in compare_cols:
            left = work.loc[overlap_idx, col]
            right = existing.loc[overlap_idx, col]
            changed_mask |= ~(left.eq(right) | (left.isna() & right.isna()))

        changed_idx = changed_mask[changed_mask].index
        changed_rows = work.loc[changed_idx].reset_index()

        if not new_rows.empty:
            new_rows = _ensure_datetime(new_rows, ["created_at", "updated_at"])
            records = [
                (
                    row.content_id,
                    row.title,
                    _to_python(row.firstimage),
                    _to_python(row.firstimage2),
                    _to_python(row.category_code),
                    _to_python(row.category_name),
                    _to_python(row.created_at),
                    _to_python(row.updated_at),
                )
                for row in new_rows.itertuples(index=False)
            ]
            if records:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        INSERT INTO tourist_spot (
                            content_id, title, firstimage, firstimage2,
                            category_code, category_name, created_at, updated_at
                        )
                        VALUES %s
                        ON CONFLICT (content_id) DO NOTHING
                        """,
                        records,
                        page_size=1000,
                    )
                print(f"[OK] tourist_spot 신규 {len(records):,}건")

        if not changed_rows.empty:
            changed_rows = _ensure_datetime(changed_rows, ["created_at", "updated_at"])
            params = [
                (
                    row.title,
                    _to_python(row.firstimage),
                    _to_python(row.firstimage2),
                    _to_python(row.category_code),
                    _to_python(row.category_name),
                    _to_python(row.updated_at),
                    row.content_id,
                )
                for row in changed_rows.itertuples(index=False)
            ]
            if params:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        UPDATE tourist_spot
                           SET title = %s,
                               firstimage = %s,
                               firstimage2 = %s,
                               category_code = %s,
                               category_name = %s,
                               updated_at = %s
                         WHERE content_id = %s
                        """,
                        params,
                        page_size=1000,
                    )
                print(f"[OK] tourist_spot 갱신 {len(params):,}건")


def _build_detail_bundle(
    spot_detail: Optional[pd.DataFrame],
    info_df: Optional[pd.DataFrame],
    intro_df: Optional[pd.DataFrame],
    code_df: Optional[pd.DataFrame],
) -> pd.DataFrame:
    if spot_detail is None or spot_detail.empty:
        return pd.DataFrame()

    base = spot_detail.copy()
    if "content_id" not in base.columns:
        raise ValueError("tour_spot_detail dataframe must contain content_id column")

    base["content_id"] = base["content_id"].astype(str).str.strip().str.lstrip("0")

    base = base.rename(columns={"zipcode": "zip_code"})
    base["map_x"] = pd.to_numeric(base.get("map_x"), errors="coerce")
    base["map_y"] = pd.to_numeric(base.get("map_y"), errors="coerce")
    base["address_code"] = base["address_code"].astype(str).str.strip().str.lstrip("0")

    if code_df is not None and not code_df.empty and "address_code" in base.columns:
        sig_lookup = code_df[["code", "name"]].rename(columns={"code": "address_code", "name": "sigungu_name"})
        base = base.merge(sig_lookup, on="address_code", how="left")
    else:
        base["sigungu_name"] = None

    base = base.drop_duplicates(subset=["content_id"], keep="first")

    intro = pd.DataFrame()
    if intro_df is not None and not intro_df.empty:
        intro = intro_df.copy()
        intro["content_id"] = intro["content_id"].astype(str).str.strip().str.lstrip("0")
        intro = intro.rename(
            columns={
                "intro_serialnum": "intro_serial_num",
                "contenttypeid": "content_type_id",
            }
        )
        intro["intro_serial_num"] = pd.to_numeric(intro["intro_serial_num"], errors="coerce").astype("Int64")
        for col in ["is_parking", "is_baby_carriage", "is_pet", "is_credit_card"]:
            if col in intro.columns:
                intro[col] = pd.to_numeric(intro[col], errors="coerce").astype("Int64")

    info = pd.DataFrame()
    if info_df is not None and not info_df.empty:
        info = info_df.copy()

        info["content_id"] = info["content_id"].astype(str).str.strip().str.lstrip("0")
        info = info.rename(
            columns={
                "serialnum": "info_serial_num",
                "infoname": "info_name",
                "infotext": "info_text",
            }
        )
        info["info_serial_num"] = info["info_serial_num"].astype(str).str.strip()
        info.loc[info["info_serial_num"] == "", "info_serial_num"] = pd.NA

    merged = base.merge(intro, on="content_id", how="left")
    if not info.empty:
        merged = merged.merge(info, on="content_id", how="left")

    for col in ["tel", "restdate", "useseason", "usetime", "info_name", "info_text"]:
        if col in merged.columns:
            merged[col] = merged[col].where(merged[col].notna(), None)

    for col in ["is_parking", "is_baby_carriage", "is_pet", "is_credit_card"]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").astype("Int64")

    datetime_cols = ["created_at", "updated_at"]
    merged = _ensure_datetime(merged, datetime_cols)

    column_order = [
        "content_id",
        "address_code",
        "sigungu_name",
        "zip_code",
        "address",
        "map_x",
        "map_y",
        "intro_serial_num",
        "content_type_id",
        "tel",
        "restdate",
        "useseason",
        "usetime",
        "is_parking",
        "is_baby_carriage",
        "is_pet",
        "is_credit_card",
        "info_serial_num",
        "info_name",
        "info_text",
        "created_at",
        "updated_at",
    ]

    for col in column_order:
        if col not in merged.columns:
            merged[col] = None

    return merged[column_order]


def ingest_tour_detail(
    spot_detail: Optional[pd.DataFrame],
    info_df: Optional[pd.DataFrame],
    intro_df: Optional[pd.DataFrame],
    code_df: Optional[pd.DataFrame],
) -> None:
    bundle = _build_detail_bundle(spot_detail, info_df, intro_df, code_df)
    if bundle.empty:
        return

    ensure_tour_tables()

    with pg_connect() as conn:
        existing = pd.read_sql(
            """
            SELECT content_id, intro_serial_num, info_serial_num, address_code, sigungu_name, zip_code, address,
                   map_x, map_y, created_at, updated_at, content_type_id, tel, restdate, useseason, usetime,
                   is_parking, is_baby_carriage, is_pet, is_credit_card, info_name, info_text
              FROM tourist_spot_detail
            """,
            conn,
        )

        key_cols = ["content_id", "intro_serial_num", "info_serial_num"]
        bundle = bundle.drop_duplicates(subset=key_cols).set_index(key_cols)
        existing = existing.drop_duplicates(subset=key_cols).set_index(key_cols)

        new_idx = bundle.index.difference(existing.index)
        new_rows = bundle.loc[new_idx].reset_index()

        overlap_idx = bundle.index.intersection(existing.index)
        compare_cols = [
            "address_code",
            "sigungu_name",
            "zip_code",
            "address",
            "map_x",
            "map_y",
            "content_type_id",
            "tel",
            "restdate",
            "useseason",
            "usetime",
            "is_parking",
            "is_baby_carriage",
            "is_pet",
            "is_credit_card",
            "info_name",
            "info_text",
        ]
        changed_mask = pd.Series(False, index=overlap_idx)
        for col in compare_cols:
            left = bundle.loc[overlap_idx, col]
            right = existing.loc[overlap_idx, col]
            changed_mask |= ~(left.eq(right) | (left.isna() & right.isna()))

        changed_idx = changed_mask[changed_mask].index
        changed_rows = bundle.loc[changed_idx].reset_index()

        if not new_rows.empty:
            new_rows = _ensure_datetime(new_rows, ["created_at", "updated_at"])
            records = [
                (
                    row.content_id,
                    _to_python(row.address_code),
                    _to_python(row.sigungu_name),
                    _to_python(row.zip_code),
                    _to_python(row.address),
                    _to_python(row.map_x),
                    _to_python(row.map_y),
                    _to_python(row.intro_serial_num),
                    _to_python(row.content_type_id),
                    _to_python(row.tel),
                    _to_python(row.restdate),
                    _to_python(row.useseason),
                    _to_python(row.usetime),
                    _to_python(row.is_parking),
                    _to_python(row.is_baby_carriage),
                    _to_python(row.is_pet),
                    _to_python(row.is_credit_card),
                    _to_python(row.info_serial_num),
                    _to_python(row.info_name),
                    _to_python(row.info_text),
                    _to_python(row.created_at),
                    _to_python(row.updated_at),
                )
                for row in new_rows.itertuples(index=False)
            ]
            if records:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        INSERT INTO tourist_spot_detail (
                            content_id, address_code, sigungu_name, zip_code, address, map_x, map_y,
                            intro_serial_num, content_type_id, tel, restdate, useseason, usetime,
                            is_parking, is_baby_carriage, is_pet, is_credit_card,
                            info_serial_num, info_name, info_text, created_at, updated_at
                        )
                        VALUES %s
                        ON CONFLICT (content_id, intro_serial_num, info_serial_num) DO NOTHING
                        """,
                        records,
                        page_size=1000,
                    )
                print(f"[OK] tourist_spot_detail 신규 {len(records):,}건")

        if not changed_rows.empty:
            changed_rows = _ensure_datetime(changed_rows, ["created_at", "updated_at"])
            params = [
                (
                    _to_python(row.address_code),
                    _to_python(row.sigungu_name),
                    _to_python(row.zip_code),
                    _to_python(row.address),
                    _to_python(row.map_x),
                    _to_python(row.map_y),
                    _to_python(row.content_type_id),
                    _to_python(row.tel),
                    _to_python(row.restdate),
                    _to_python(row.useseason),
                    _to_python(row.usetime),
                    _to_python(row.is_parking),
                    _to_python(row.is_baby_carriage),
                    _to_python(row.is_pet),
                    _to_python(row.is_credit_card),
                    _to_python(row.info_name),
                    _to_python(row.info_text),
                    _to_python(row.updated_at),
                    row.content_id,
                    _to_python(row.intro_serial_num),
                    _to_python(row.info_serial_num),
                    _to_python(row.info_serial_num),
                )
                for row in changed_rows.itertuples(index=False)
            ]
            if params:
                with conn.cursor() as cur:
                    execute_batch(
                        cur,
                        """
                        UPDATE tourist_spot_detail
                           SET address_code = %s,
                               sigungu_name = %s,
                               zip_code = %s,
                               address = %s,
                               map_x = %s,
                               map_y = %s,
                               content_type_id = %s,
                               tel = %s,
                               restdate = %s,
                               useseason = %s,
                               usetime = %s,
                               is_parking = %s,
                               is_baby_carriage = %s,
                               is_pet = %s,
                               is_credit_card = %s,
                               info_name = %s,
                               info_text = %s,
                               updated_at = %s
                         WHERE content_id = %s
                           AND intro_serial_num = %s
                           AND ((info_serial_num IS NULL AND %s IS NULL) OR info_serial_num = %s)
                        """,
                        params,
                        page_size=1000,
                    )
                print(f"[OK] tourist_spot_detail 갱신 {len(params):,}건")


def main(write_to_disk: bool = False, raw_dir: Path = RAW_DIR) -> None:
    """관광지 관련 전처리와 DB 적재를 한 번에 실행한다."""
    print("⭐⭐")
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from preprocess import tour as preprocess_tour
    from preprocess import details as preprocess_details

    ensure_tour_tables()
    code_df = _load_code_table()

    frames = preprocess_tour.main(write_to_disk=write_to_disk, raw_dir=RAW_DIR)

    tour_spot_df = frames.get("tour_spot")
    tour_detail_df = frames.get("tour_spot_detail")

    ingest_tour_spot(tour_spot_df, code_df)

    info_df, intro_df = preprocess_details.main(write_to_disk=write_to_disk, raw_dir=RAW_DIR)
    ingest_tour_detail(tour_detail_df, info_df, intro_df, code_df)


if __name__ == "__main__":
    main(write_to_disk=False, raw_dir=RAW_DIR)

