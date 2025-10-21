"""법정동 코드(ldongCode2) API를 호출해 지역 코드 CSV를 만든다."""

import os, sys
from datetime import datetime
import pandas as pd

from paths import RAW_DIR

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
목표
- /ldongCode2 (법정동코드조회)로
  1) 시도 목록         -> ldong_sido.csv
  2) 각 시도의 시군구  -> ldong_sigungu.csv
  3) (옵션) 각 시군구의 읍/면/동 전체 -> ldong_emd.csv  (lDongListYn=Y)

주의
- SERVICE_KEY는 반드시 '디코딩 키'(/ 포함)를 .env에 넣어 사용하세요.
- KorService2이므로 메서드명은 끝이 2인 버전(/ldongCode2).
"""

def run_ldong_code(client):
    """서울 지역 코드를 호출해 CSV로 저장한다."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------------------------------------------------
    # 1) 시도 목록 (lDongRegnCd 미지정)
    # ---------------------------------------------------------
    sido_items = client.get_all_pages("ldongCode2", params={}, num_of_rows=100)
    
    # 어떤 필드가 오든 원본을 보존하고, 우리가 쓰는 컬럼만 추가로 정규화
    df_sido = pd.DataFrame(sido_items)
    # 추정 필드명: lDongRegnCd(코드), lDongRegnNm(이름) — 문서/응답에 따라 달라질 수 있으니
    # 안전하게 컬럼 존재 여부 확인
    code_col = "lDongRegnCd" if "lDongRegnCd" in df_sido.columns else "code"
    name_col = "lDongRegnNm" if "lDongRegnNm" in df_sido.columns else "name"
    df_sido.rename(columns={code_col: "sidoCode", name_col: "sidoName"}, inplace=True)
    
    # 저장 생략 --> 서울로 범위 축소
    # 서울(11)만 남기기
    df_sido = df_sido[df_sido["sidoCode"].astype(str).str.strip().str.zfill(2) == "11"].reset_index(drop=True)


    # ---------------------------------------------------------
    # 2) 각 시도의 시군구 목록 (lDongRegnCd=시도코드)
    # ---------------------------------------------------------
    sigungu_rows = []
    for _, row in df_sido.iterrows():
        ac = row["sidoCode"]
        aname = row["sidoName"]
        items = client.get_all_pages(
            "ldongCode2",
            params={"lDongRegnCd": ac},  # ← 시도코드 지정 시 해당 시군구 목록 반환
            num_of_rows=100,
        )
        for it in items or []:
            # 동적으로 필드 추출
            scode = it.get("lDongRegnCd", it.get("code"))
            sname = it.get("lDongRegnNm", it.get("name"))
            sigungu_rows.append(
                {
                    "sidoCode": ac,
                    "sigunguCode": scode,
                    "sigunguName": sname,
                }
            )
        print(f"[INFO] 시도 {ac}({aname}) → 시군구 {len(items or [])}건")

    df_sigungu = pd.DataFrame(sigungu_rows)
    df_sigungu = df_sigungu[["sigunguCode","sigunguName"]]
    df_sigungu["created_at"] = timestamp
    df_sigungu["updated_at"] = timestamp

    save_path = RAW_DIR / "ldong_sigungu.csv"
    df_sigungu.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"[OK] ldong_sigungu.csv 저장 ({len(df_sigungu)}건)")

