"""detailIntro API를 호출해 관광지 소개 정보를 수집한다."""

import os, sys
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

def run_detailIntro(client):
    """detailIntro API 응답을 병합해 CSV로 저장한다."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # content_id = "126130"
    contentid_list = []
    df = pd.read_csv(RAW_DIR / "tourist_spot_seoul.csv")
    contentid_list = df['contentid'].astype(str).tolist()

    # contentTypeId는 12(관광지)로 고정
    content_type_id = "12"

    dataframe = pd.DataFrame()

    try:
        for content_id in contentid_list:
            items_ = client.get_all_pages("detailIntro2", params={
                "contentId": content_id,
                "contentTypeId" : content_type_id
            }, num_of_rows=100)
            _normalise_tel_field(items_)

            save_path = RAW_DIR / "detail_intro.csv"

            df_ = pd.DataFrame(items_)            
            dataframe = pd.concat([dataframe, df_], ignore_index=True)

    except Exception as e:
        print(f"[ERROR] API 호출 실패: {e}")
        return


    # 어떤 필드가 오든 원본을 보존하고, 우리가 쓰는 컬럼만 추가로 정규화
    try:
        dataframe.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"[OK] {len(df)}건 저장 완료 → {save_path}")
    except Exception as e:
        print(f"[ERROR] CSV 저장 실패: {e}")
