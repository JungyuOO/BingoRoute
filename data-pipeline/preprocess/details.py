"""관광지 상세/소개 CSV를 정규화해 DB 적재 형태로 가공한다."""

import html
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from paths import RAW_DIR, DB_DATA_DIR  # directories anchored at project root


def read_csv(path: Path) -> pd.DataFrame:
    """UTF-8/CP949 양쪽 인코딩을 감안해 CSV를 안전하게 읽는다."""
    read_kwargs = {"keep_default_na": False}
    try:
        return pd.read_csv(path, encoding="utf-8", **read_kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949", **read_kwargs)


def clean_text(value: str | float) -> str | None:
    if pd.isna(value):
        return None

    text = str(value)
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\r", "").replace("\t", " ")

    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]

    if not lines:
        return None

    return "\n".join(lines)


def _format_phone_digits(digits: str) -> str:
    if not digits:
        return ""

    if re.fullmatch(r"(15|16|18)\d{6}", digits):
        return f"{digits[:4]}-{digits[4:]}"

    if digits.startswith("050"):
        if len(digits) >= 12:
            return f"{digits[:4]}-{digits[4:8]}-{digits[8:]}"
        if len(digits) == 11:
            return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"

    if digits == "120":
        return "02-120"

    if digits.startswith("02"):
        rest = digits[2:]
        if len(rest) >= 8:
            return f"02-{rest[:-4]}-{rest[-4:]}"
        if len(rest) == 7:
            return f"02-{rest[:3]}-{rest[3:]}"
        if len(rest) >= 4:
            return f"02-{rest[:-4]}-{rest[-4:]}"
        return f"02-{rest}"

    if digits.startswith("0"):
        area = digits[:3]
        local = digits[3:]
        if len(local) >= 8:
            return f"{area}-{local[:-4]}-{local[-4:]}"
        if len(local) == 7:
            return f"{area}-{local[:3]}-{local[3:]}"
        if len(local) >= 4:
            return f"{area}-{local}"
        return f"{area}-{local}"

    if len(digits) == 8:
        return f"{digits[:4]}-{digits[4:]}"

    if len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"

    if len(digits) > 4:
        return f"{digits[:-4]}-{digits[-4:]}"

    return digits


def _expand_suffix_range(base_digits: str, end_suffix: str) -> List[str]:
    base_digits = re.sub(r"\D", "", base_digits or "")
    end_digits = re.sub(r"\D", "", end_suffix or "")

    if not base_digits:
        return []

    if not end_digits:
        return [_format_phone_digits(base_digits)]

    width = max(1, min(len(base_digits), len(end_digits)))
    start_segment = base_digits[-width:]

    try:
        start_num = int(start_segment)
        end_num = int(end_digits)
    except ValueError:
        return [_format_phone_digits(base_digits)]

    if end_num < start_num:
        return [_format_phone_digits(base_digits)]

    prefix = base_digits[:-width]
    numbers: List[str] = []
    for num in range(start_num, end_num + 1):
        digits = f"{prefix}{num:0{width}d}"
        numbers.append(_format_phone_digits(digits))

    return numbers


def _expand_flat_digit_range(digits: str) -> List[str]:
    if not digits.startswith("02"):
        return []
    if len(digits) < 10:
        return []

    start_char = digits[-2]
    end_char = digits[-1]
    if not (start_char.isdigit() and end_char.isdigit()):
        return []

    start = int(start_char)
    end = int(end_char)
    if end <= start or end - start > 9:
        return []

    prefix = digits[:-2]
    expanded: List[str] = []
    for suffix in range(start, end + 1):
        expanded.append(_format_phone_digits(prefix + str(suffix)))
    return expanded


_TOKEN_PATTERN = re.compile(r"\d[\d\s\-\(\)~]*\d")
_LABEL_PATTERN = re.compile(r"\b(Tel|TEL|tel|Fax|FAX|fax)\b[:\s]*")


def _sanitize_phone_length(value: object) -> Optional[str]:
    if pd.isna(value):
        return None
    phone = str(value).strip()
    if not phone:
        return None
    digits = re.sub(r'\D', '', phone)
    return phone if len(digits) >= 5 else None


def _extract_phone_segments(text: str) -> List[Tuple[str, str]]:
    if not text:
        return []

    cleaned = _LABEL_PATTERN.sub("", text)
    tokens = _TOKEN_PATTERN.findall(cleaned)

    segments: List[Tuple[str, str]] = []
    for token in tokens:
        raw = token.strip()
        normalized = re.sub(r"[()\s]", "", raw)
        normalized = re.sub(r"[^\d\-~]", "", normalized)

        if not re.search(r"\d", normalized):
            continue

        if "~" in normalized:
            base_part, suffix_part = normalized.split("~", 1)
            numbers = _expand_suffix_range(base_part, suffix_part)
            if not numbers:
                continue
            for number in numbers:
                segments.append((raw, number))
            continue

        digits = re.sub(r"\D", "", normalized)
        if not digits:
            continue

        flattened = _expand_flat_digit_range(digits)
        if flattened:
            for number in flattened:
                segments.append((raw, number))
            continue

        segments.append((raw, _format_phone_digits(digits)))

    seen = set()
    dedup: List[Tuple[str, str]] = []
    for raw, tel in segments:
        if tel not in seen:
            seen.add(tel)
            dedup.append((raw, tel))

    return dedup


def _load_tourist_contacts(raw_dir: Path = RAW_DIR) -> Dict[str, Set[str]]:
    path = raw_dir / "tourist_spot_seoul.csv"
    if not path.exists():
        return {}

    tour_df = read_csv(path)
    if "contentid" not in tour_df.columns or "tel" not in tour_df.columns:
        return {}

    contact_map: Dict[str, Set[str]] = {}
    for contentid, tel in tour_df[["contentid", "tel"]].itertuples(index=False):
        cid = str(contentid).strip().lstrip("0")
        tel_text = str(tel).strip()
        if not cid or not tel_text or tel_text.lower() == "nan":
            continue
        segments = _extract_phone_segments(tel_text)
        numbers = [number for _, number in segments if number]
        if not numbers:
            continue
        contact_map.setdefault(cid, set()).update(numbers)

    return contact_map


def prep_info(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "contentid",
        "contenttypeid",
        "serialnum",
        "infoname",
        "infotext",
        "fldgubun",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"detailinfo requires columns: {sorted(missing)}")

    out = df[list(required)].copy()
    out = out.drop(columns=["fldgubun"], errors="ignore")
    out["infotext"] = out["infotext"].apply(clean_text)
    out = out.dropna(subset=["contentid", "infotext"]).reset_index(drop=True)

    out["contentid"] = out["contentid"].astype(str).str.strip().str.lstrip("0")
    out["serialnum"] = out["serialnum"].astype(str).str.strip()
    out = out.rename(columns={"serialnum": "info_serial_num","contentid": "content_id"})
    out["infoname"] = out["infoname"].astype(str).str.strip()

    if out.duplicated(subset=["content_id", "info_serial_num"]).any():
        raise ValueError("Duplicate (content_id, info_serial_num) rows detected in detailinfo.")
    if out["infoname"].isna().any():
        raise ValueError("detailinfo contains null infoname values.")

    return out[[
        "content_id",
        "info_serial_num",
        "infoname",
        "infotext",
    ]]


# detailintro 테이블 전처리
def prep_intro(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "contentid",
        "contenttypeid",
        "infocenter",
        "restdate",
        "expguide",
        "expagerange",
        "accomcount",
        "useseason",
        "usetime",
        "parking",
        "chkbabycarriage",
        "chkpet",
        "chkcreditcard",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"detailintro requires columns: {sorted(missing)}")

    out = df.copy()
    out = out.drop(columns=["heritage1", "heritage2", "heritage3", "opendate"], errors="ignore")
    out = out.dropna(subset=["contentid", "contenttypeid"])

    text_cols = [
        "restdate",
        "useseason",
        "usetime",
        "parking",
    ]
    for col in text_cols:
        if col in out.columns:
            out[col] = out[col].apply(clean_text)

    out["contentid"] = out["contentid"].astype(str).str.strip().str.lstrip("0")
    out["contenttypeid"] = out["contenttypeid"].astype(str).str.strip()

    # infocenter 컬럼에서 복수 전화번호 추출
    def split_multiple_infocenter(value: Optional[str]) -> List[Tuple[Optional[str], Optional[str]]]:
        if pd.isna(value) or value == "":
            return []

        parts = re.split(r"<br>|\\r\\n|\\n|,", str(value))
        results: List[Tuple[Optional[str], Optional[str]]] = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            segments = _extract_phone_segments(part)
            if not segments:
                text_only = clean_text(part) or part
                results.append((text_only, None))
                continue

            name = part
            for raw, _ in segments:
                pattern = re.escape(raw)
                pattern = pattern.replace(r"\-", r"\s*-\s*")
                pattern = pattern.replace(r"\~", r"\s*~\s*")
                name = re.sub(pattern, "", name)

            name = re.sub(r"\s*~\s*\d+\b", "", name)
            name = re.sub(r"\s{2,}", " ", name)
            name = name.strip(" -~;/,")
            if name.startswith("(") and name.endswith(")"):
                name = name[1:-1].strip()
            name = name.strip(":") if name else None
            name = name if name else None

            for _, tel in segments:
                results.append((name, tel))

        return results

    out["infocenter_tel"] = out["infocenter"].apply(split_multiple_infocenter)
    out = out.explode("infocenter_tel", ignore_index=True)

    if out["infocenter_tel"].notna().any():
        unpack = out.loc[out["infocenter_tel"].notna(), "infocenter_tel"].apply(pd.Series)
        unpack.columns = ["infocenter", "tel"]
        out.loc[unpack.index, ["infocenter", "tel"]] = unpack
    else:
        out["infocenter"] = None
        out["tel"] = None

    out = out.drop(columns=["infocenter_tel"])
    out["tel"] = out["tel"].apply(_sanitize_phone_length)

    tourist_contacts = _load_tourist_contacts()
    if tourist_contacts:
        existing_numbers: Dict[str, Set[str]] = {}
        for contentid, group in out.groupby("contentid"):
            numbers = {
                str(tel)
                for tel in group["tel"].dropna()
                if str(tel).strip()
            }
            existing_numbers[contentid] = numbers

        additions = []
        for contentid, numbers in tourist_contacts.items():
            if not numbers:
                continue
            if existing_numbers.get(contentid):
                continue
            mask = out["contentid"] == contentid
            if not mask.any():
                continue
            base_row = out.loc[mask].iloc[0].copy()
            for tel in sorted(numbers):
                new_row = base_row.copy()
                new_row["tel"] = tel
                additions.append(new_row)
        if additions:
            out = pd.concat([out, pd.DataFrame(additions)], ignore_index=True)

    out = out.reset_index(drop=True)

    # id당 복수 row에 대해 serialnum 부여
    out["intro_serialnum"] = out.groupby("contentid").cumcount().astype(int)

    # parking, chkbabycarriage, chkpet, chkcreditcard 컬럼을 Y/N 값으로 변환, 그 외 값 detail로 처리
    # 부정/긍정 패턴
    NEG_PAT = re.compile(r"(주차\s*장\s*)?(없음|없습니다|없어|없고|불가|미운영|금지|출입\s*통제)")
    POS_PAT = re.compile(r"(주차\s*장|주차\s*가능|이용\s*가능|공영\s*주차장|인근\s*.*주차장|유료|무료|할인|30\s*분|1\s*시간)")

    def normalize_parking(text: Optional[str], strict_no: bool = False) -> Optional[int]:
        """입력 텍스트를 주차 가능 여부(1/0) 또는 결측(pd.NA)으로 변환."""
        if text is None or (isinstance(text, float) and pd.isna(text)):
            return pd.NA

        s = str(text).strip()
        if not s:
            return pd.NA

        s_for_match = re.sub(r"<\s*br\s*/?\s*>", " ", s, flags=re.I)
        s_for_match = re.sub(r"\s+", " ", s_for_match).strip()

        has_neg = bool(NEG_PAT.search(s_for_match))
        has_pos = bool(POS_PAT.search(s_for_match)) or ("주차장" in s_for_match)

        if strict_no:
            status = 0 if has_neg else (1 if has_pos else None)
        else:
            status = 1 if has_pos else (0 if has_neg else None)

        return pd.NA if status is None else status

    # 불가/없음 판정 키워드(하나라도 포함되면 0)
    NEG_KWS = [
        "불가", "안됨", "안 돼", "안되", "금지", "불편",
        "없음", "없습니다", "없어요", "무", "미제공", "대여 불가"
    ]
    # 긍/부 단순표현: note에서 제거
    GENERIC_KWS = [
        "가능", "가능함", "가능합니다", "가능해요",
        "불가", "없음", "없습니다", "없어요",
        "있음", "있습니다", "있어요",
        "대여 가능", "대여 불가", "주차 가능", "주차가능", "주차 불가", "주차불가", "주차장",
        "O", "o", "X", "x"
    ]

    neg_pat = re.compile("|".join(map(re.escape, NEG_KWS)))
    generic_pat = re.compile("|".join(map(re.escape, GENERIC_KWS)))

    parking_place_pattern = re.compile(r'\S*주차장(?: 이용)?', re.IGNORECASE)


    out["is_parking"] = out["parking"].apply(lambda v: normalize_parking(v, strict_no=True))
    out["is_parking"] = out["is_parking"].astype("Int64")

    # chkbabycarriage, chkpet, chkcreditcard 컬럼 처리
    yn_mapping = {
        "chkbabycarriage": "is_baby_carriage",
        "chkpet": "is_pet",
        "chkcreditcard": "is_credit_card"
    }

    def normalize_yn_cell(val: object) -> Optional[int]:
        if pd.isna(val):
            return pd.NA
        s = str(val).strip()
        if not s:
            return pd.NA
        return 0 if neg_pat.search(s) else 1

    for src_col, status_col in yn_mapping.items():
        out[status_col] = out[src_col].apply(normalize_yn_cell).astype("Int64")

    out = out.drop(columns=["parking", *yn_mapping.keys()], errors="ignore")

    out = out.drop(columns=["infocenter", "expguide", "expagerange", "accomcount"], errors="ignore")

    out = out.rename(columns={"contentid": "content_id"})

    return out[[
        "content_id",
        "intro_serialnum",
        "contenttypeid",
        "tel", # --> 모달에 작성
        "restdate", # --> 모달에 작성
        "useseason", # --> 모달에 작성
        "usetime", # --> 모달에 작성
        "is_parking", # --> 모달에 작성
        "is_baby_carriage", # --> 모달에 작성
        "is_pet", # --> 모달에 작성
        "is_credit_card", # --> 모달에 작성
    ]]


def preprocess_all(raw_dir: Path = RAW_DIR) -> Tuple[pd.DataFrame | None, pd.DataFrame | None]:
    info_df: pd.DataFrame | None = None
    intro_df: pd.DataFrame | None = None

    info_path = raw_dir / "detail_info.csv"
    if info_path.exists():
        info_df = prep_info(read_csv(info_path))

    intro_path = raw_dir / "detail_intro.csv"
    if intro_path.exists():
        intro_df = prep_intro(read_csv(intro_path))

    return info_df, intro_df


def main(
    write_to_disk: bool = False, raw_dir: Path = RAW_DIR
) -> Tuple[pd.DataFrame | None, pd.DataFrame | None]:
    info_df, intro_df = preprocess_all(raw_dir)

    if write_to_disk:
        DB_DATA_DIR.mkdir(parents=True, exist_ok=True)

        for filename, df in (
            ("pre_detail_info.csv", info_df),
            ("pre_detail_intro.csv", intro_df),
        ):
            if df is None:
                continue
            df.to_csv(DB_DATA_DIR / filename, index=False, encoding="utf-8-sig")
            print(f"[OK] {filename} saved")

    return info_df, intro_df


if __name__ == "__main__":
    main(write_to_disk=True)

