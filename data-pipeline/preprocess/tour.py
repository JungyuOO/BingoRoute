"""관광지 기본/상세 데이터를 DB 적재용 형태로 전처리하는 모듈."""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paths import RAW_DIR, DB_DATA_DIR

# csv 읽기 및 날짜 변환
def read_csv(path: Path) -> pd.DataFrame:
    """UTF-8/CP949 인코딩 차이를 감안해 관광지 CSV를 읽어온다."""
    read_kwargs = {"keep_default_na": False}
    try:
        df = pd.read_csv(path, encoding="utf-8", **read_kwargs)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949", **read_kwargs)

    df = df.rename(columns={"createdtime": "created_at", "modifiedtime": "updated_at"})
    for col in ("created_at", "updated_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%Y%m%d%H%M%S", errors="coerce")
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            df[col] = pd.NaT
    return df



def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["contentid"] = out["contentid"].astype(str).str.strip()
    return out

# 테이블1 관광지 기본 정보(카드기재)
# DB에서 codetable 찾아서 분류코드 매핑 필요
def tour_spot(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["contentid", "title", "firstimage", "firstimage2", "lclsSystm3", "created_at", "updated_at"]
    out = _normalise(df)[cols].dropna(subset=["contentid"]).drop_duplicates(subset=["contentid"])

    out = out.rename(columns={"contentid": "content_id", "lclsSystm3": "category_code"})
    out["category_code"] = out["category_code"].astype(str).str.strip().str.lstrip("0")

    numeric_cols = ["firstimage", "firstimage2"]
    for col in numeric_cols:
        out[col] = out[col].astype(str).str.strip()

    return out

# 테이블2 관광지 디테일 정보(카드 클릭 -> 모달 기재)
# DB에서 codetable 찾아서 분류코드 매핑 필요
def tour_spot_detail(df: pd.DataFrame) -> pd.DataFrame:
    base_cols = [
        "contentid",
        "lDongSignguCd",
        "addr1",
        "addr2",
        "zipcode",
        "mapx",
        "mapy",
        "created_at",
        "updated_at",
    ]

    available_cols = [col for col in base_cols if col in df.columns]
    if "contentid" not in available_cols:
        raise ValueError("tour_spot_detail requires contentid column")

    out = _normalise(df)[available_cols]
    out = out.dropna(subset=["contentid"]).drop_duplicates(subset=["contentid"])

    out = out.rename(
        columns={
            "contentid": "content_id",
            "mapx": "map_x",
            "mapy": "map_y",
            "lDongSignguCd": "address_code",
        }
    )

    for col in ("addr1", "addr2"):
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip().replace({"": None})

    out["map_x"] = pd.to_numeric(out.get("map_x"), errors="coerce")
    out["map_y"] = pd.to_numeric(out.get("map_y"), errors="coerce")
    out["map_x"] = out["map_x"].apply(lambda v: f"{v:.6f}" if pd.notna(v) else None)
    out["map_y"] = out["map_y"].apply(lambda v: f"{v:.6f}" if pd.notna(v) else None)

    if "addr1" in out.columns:
        addr1_parts = out["addr1"].fillna("").str.split()
        base_addr = addr1_parts.apply(lambda tokens: tokens[2] if len(tokens) > 2 else "")
    else:
        base_addr = pd.Series([""] * len(out), index=out.index)

    addr2_series = out["addr2"].replace("", pd.NA).fillna("") if "addr2" in out.columns else pd.Series([""] * len(out), index=out.index)
    out["address"] = (base_addr + " " + addr2_series).str.strip()
    out = out.drop(columns=["addr1", "addr2"], errors="ignore")

    out["zipcode"] = out.get("zipcode", pd.Series([None] * len(out))).apply(
        lambda v: None if pd.isna(v) or str(v).strip() == "" else str(v).strip()
    )

    return out


TourFrames = Dict[str, Optional[pd.DataFrame]]


def preprocess_all(raw_dir) -> TourFrames:
    frames: TourFrames = {
        "tour_spot": None,
        "tour_spot_detail": None,
    }

    tourist_spot_path = raw_dir / "tourist_spot_seoul.csv"

    if not tourist_spot_path.exists():
        return frames

    raw_df = read_csv(tourist_spot_path)

    frames["tour_spot"] = tour_spot(raw_df)
    frames["tour_spot_detail"] = tour_spot_detail(raw_df)

    

    return frames


def main(write_to_disk: bool = False, raw_dir: Path = RAW_DIR) -> TourFrames:
    frames = preprocess_all(raw_dir)

    if write_to_disk:
        DB_DATA_DIR.mkdir(parents=True, exist_ok=True)
        file_map = [
            ("tour_spot.csv", frames["tour_spot"]),
            ("tour_spot_detail.csv", frames["tour_spot_detail"]),
        ]

        for filename, df in file_map:
            if df is None:
                continue
            df.to_csv(DB_DATA_DIR / filename, index=False, encoding="utf-8-sig")
            print(f"[OK] {filename} 저장")

    return frames


if __name__ == "__main__":
    main(write_to_disk=False)
