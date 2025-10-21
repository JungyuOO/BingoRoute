"""분류/지역 코드 테이블 원본 CSV를 정규화하는 전처리 모듈."""

import pandas as pd
from datetime import datetime
from pathlib import Path

from paths import RAW_DIR, DB_DATA_DIR


def read_csv(path: Path) -> pd.DataFrame:
    read_kwargs = {"keep_default_na": False}
    try:
        return pd.read_csv(path, encoding="utf-8", **read_kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949", **read_kwargs)


def _validate_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """타임스탬프 컬럼이 없으면 채우고(서울 기준) tz-aware 값은 일괄 변환한다."""

    now_seoul = (
        pd.Timestamp.now(tz="UTC")
        .floor("s")
        .tz_convert("Asia/Seoul")
        .tz_localize(None)
    )

    for col in ("created_at", "updated_at"):
        if col not in df.columns:
            df[col] = now_seoul
            continue

        converted = pd.to_datetime(df[col], errors="coerce")
        if isinstance(converted.dtype, pd.DatetimeTZDtype):
            converted = converted.dt.tz_convert("Asia/Seoul").dt.tz_localize(None)

        df[col] = converted
        df.loc[df[col].isna(), col] = now_seoul

    return df


def prep_sigungu(df: pd.DataFrame) -> pd.DataFrame:
    required = {"sigunguCode", "sigunguName", "created_at", "updated_at"}
    if not required.issubset(df.columns):
        raise ValueError(
            "ld_sigungu 컬럼은 ['sigunguCode','sigunguName','created_at','updated_at'] 형태여야 합니다."
        )

    out = df[["sigunguCode", "sigunguName", "created_at", "updated_at"]].copy()
    out["sigunguCode"] = out["sigunguCode"].astype(str).str.strip().str.lstrip("0")
    out["sigunguName"] = out["sigunguName"].astype(str).str.strip()

    if not out["sigunguCode"].is_unique:
        raise ValueError("sigunguCode 중복이 있습니다.")
    if out["sigunguName"].isna().any():
        raise ValueError("sigunguName 결측이 있습니다.")

    out = _validate_timestamps(out)
    out = out.rename(columns={"sigunguCode": "code", "sigunguName": "name"})
    out["upper_code"] = "ADD"
    return out[["code", "name", "upper_code", "created_at", "updated_at"]]


def prep_cat1(df: pd.DataFrame) -> pd.DataFrame:
    need = {"code", "name", "created_at", "updated_at"}
    if not need.issubset(df.columns):
        raise ValueError("CAT1 컬럼은 ['code','name','created_at','updated_at'] 이어야 합니다.")

    out = df[["code", "name", "created_at", "updated_at"]].copy()
    out["code"] = out["code"].astype(str).str.strip()
    out["name"] = out["name"].astype(str).str.strip()

    if not out["code"].is_unique:
        raise ValueError("CAT1 code 중복이 있습니다.")

    out = _validate_timestamps(out)
    out["upper_code"] = "SYS"
    return out[["code", "name", "upper_code", "created_at", "updated_at"]]


def prep_cat2(df: pd.DataFrame) -> pd.DataFrame:
    need = {"systemCode1", "systemCode2", "systemName2", "created_at", "updated_at"}
    if not need.issubset(df.columns):
        raise ValueError(
            "CAT2 컬럼은 ['systemCode1','systemCode2','systemName2','created_at','updated_at'] 이어야 합니다."
        )

    out = df[["systemCode1", "systemCode2", "systemName2", "created_at", "updated_at"]].copy()
    for col in ("systemCode1", "systemCode2", "systemName2"):
        out[col] = out[col].astype(str).str.strip().str.replace(r"\|$", "", regex=True)
    out["systemCode2"] = out["systemCode2"].str.lstrip("0")

    if not out["systemCode2"].is_unique:
        raise ValueError("systemCode2 중복이 있습니다.")

    out = _validate_timestamps(out)
    out = out.rename(
        columns={"systemCode1": "upper_code", "systemCode2": "code", "systemName2": "name"}
    )
    out["upper_code"] = out["upper_code"].astype(str).str.strip()
    return out[["code", "name", "upper_code", "created_at", "updated_at"]]


def prep_cat3(df: pd.DataFrame) -> pd.DataFrame:
    need = {"systemCode2", "systemCode3", "systemName3", "created_at", "updated_at"}
    if not need.issubset(df.columns):
        raise ValueError(
            "CAT3 컬럼은 ['systemCode2','systemCode3','systemName3','created_at','updated_at'] 이어야 합니다."
        )

    out = df[["systemCode2", "systemCode3", "systemName3", "created_at", "updated_at"]].copy()
    for col in ("systemCode2", "systemCode3", "systemName3"):
        out[col] = out[col].astype(str).str.strip().str.replace(r"\|$", "", regex=True)
    out["systemCode2"] = out["systemCode2"].str.lstrip("0")
    out["systemCode3"] = out["systemCode3"].str.lstrip("0")

    if not out["systemCode3"].is_unique:
        raise ValueError("systemCode3 중복이 있습니다.")

    out = _validate_timestamps(out)
    out = out.rename(
        columns={"systemCode2": "upper_code", "systemCode3": "code", "systemName3": "name"}
    )
    out["upper_code"] = out["upper_code"].astype(str).str.strip()
    return out[["code", "name", "upper_code", "created_at", "updated_at"]]


def _build_root_row(code: str, name: str, timestamp: str) -> pd.DataFrame:
    root = pd.DataFrame(
        [
            {
                "code": code,
                "name": name,
                "upper_code": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        ]
    )
    return _validate_timestamps(root)


def preprocess_all(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """원본 CSV 묶음을 읽어 통합 코드 테이블 DataFrame으로 변환한다."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sigungu_df = None
    cat1_df = None
    cat2_df = None
    cat3_df = None

    sigungu_path = raw_dir / "ldong_sigungu.csv"
    if sigungu_path.exists():
        sigungu_df = prep_sigungu(read_csv(sigungu_path))

    cat1_path = raw_dir / "system_code1.csv"
    if cat1_path.exists():
        cat1_df = prep_cat1(read_csv(cat1_path))

    cat2_path = raw_dir / "system_code2.csv"
    if cat2_path.exists():
        cat2_df = prep_cat2(read_csv(cat2_path))

    cat3_path = raw_dir / "system_code3.csv"
    if cat3_path.exists():
        cat3_df = prep_cat3(read_csv(cat3_path))

    add_block = _build_root_row("ADD", "서울특별시_지역코드", timestamp)
    if sigungu_df is not None:
        add_block = pd.concat([add_block, sigungu_df], ignore_index=True)

    sys_frames = [_build_root_row("SYS", "분류코드", timestamp)]
    for frame in (cat1_df, cat2_df, cat3_df):
        if frame is not None:
            sys_frames.append(frame)
    sys_block = pd.concat(sys_frames, ignore_index=True)

    code_df = pd.concat([add_block, sys_block], ignore_index=True)
    return code_df


def main(write_to_disk: bool = False, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    code_df = preprocess_all(raw_dir)

    if write_to_disk:
        DB_DATA_DIR.mkdir(parents=True, exist_ok=True)

        code_df.to_csv(DB_DATA_DIR / "codetable.csv", index=False, encoding="utf-8-sig")
        print(f"[OK] codetable.csv 저장")

    return code_df


if __name__ == "__main__":
    main(write_to_disk=False)
