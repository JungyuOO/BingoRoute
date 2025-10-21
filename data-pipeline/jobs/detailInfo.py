"""detailInfo API를 호출해 관광지 세부 정보를 수집한다."""

import os, sys
import pandas as pd

from paths import RAW_DIR

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utill.tourapi_client import TourAPIClient

def run_detailInfo(client):
    """콘텐츠 ID 목록을 돌며 detailInfo API 응답을 CSV로 저장한다."""

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
            items_ = client.get_all_pages("detailInfo2", params={
                "contentId": content_id,
                "contentTypeId" : content_type_id
            }, num_of_rows=100)

            save_path = RAW_DIR / "detail_info.csv"

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
