"""관광지 목록(areaBasedSyncList) API를 호출해 RAW 데이터를 수집한다."""

import os
import sys
import pandas as pd

from paths import RAW_DIR

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _normalise_tel_field(items: list[dict]) -> None:
    for item in items:
        if not isinstance(item, dict):
            continue
        if "tel" not in item:
            continue
        tel_value = item["tel"]
        if tel_value is None:
            item["tel"] = None
            continue
        tel_text = str(tel_value).strip()
        item["tel"] = tel_text if tel_text else None


def run_tourist_spot(client):
    """서울시 관광지 목록 API를 호출하고 CSV로 저장한다."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    params = {"contentTypeId": "12", "lDongRegnCd": "11"}
    items = client.get_all_pages("areaBasedSyncList2", params=params, num_of_rows=100)
    _normalise_tel_field(items)

    df_ = pd.DataFrame(items)

    drop_cols = [
        "areacode",
        "sigungucode",
        "lDongRegnCd",
        "cat1",
        "cat2",
        "cat3",
        "cpyrhtDivCd",
        "mlevel",
        "showflag",
    ]
    df_.drop(drop_cols, axis=1, inplace=True)


    # 관광지 분류 코드 보정
    df_ = df_[~(df_["lclsSystm1"].isna() & df_["lclsSystm2"].isna() & df_["lclsSystm3"].isna())]

    small_ok = df_["lclsSystm3"].notna() & (df_["lclsSystm3"].str.len() >= 8)
    df_.loc[small_ok, "lclsSystm2"] = df_.loc[small_ok, "lclsSystm2"].fillna(
        df_.loc[small_ok, "lclsSystm3"].str[:-4]
    )

    middle_ok = df_["lclsSystm2"].notna() & (df_["lclsSystm2"].str.len() >= 4)
    df_.loc[middle_ok, "lclsSystm1"] = df_.loc[middle_ok, "lclsSystm1"].fillna(
        df_.loc[middle_ok, "lclsSystm2"].str[:-2]
    )

    # 분류 코드가 'AC'인 것은 제외(숙소)
    df_ = df_[df_["lclsSystm1"] != "AC"]

    df_.to_csv(RAW_DIR / "tourist_spot_seoul.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] tourist_spot_seoul.csv 저장({len(df_)}건)")
