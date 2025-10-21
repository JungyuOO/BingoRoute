"""데이터 파이프라인 전체 흐름을 실행하는 엔트리 포인트."""

import os
import argparse
from dotenv import load_dotenv

from jobs.ldongCode import run_ldong_code
from jobs.detailInfo import run_detailInfo
from jobs.lclsSystmCode import run_system_code
from jobs.areaBasedSyncList import run_tourist_spot
from jobs.detailIntro import run_detailIntro
from utill.tourapi_client import TourAPIClient
from db import ingest_base_db, ingest_tour_db
from preprocess import base, tour, details
from paths import ensure_data_dirs, ENV_FILE


def main(flag):
    """선택한 인증키(flag)에 맞춰 API 데이터를 수집·전처리·적재한다."""
    load_dotenv(dotenv_path=ENV_FILE, override=False)

    if flag == "num1":
        SERVICE_KEY = os.getenv("SERVICE_KEY1")
    elif flag == "num2":
        SERVICE_KEY = os.getenv("SERVICE_KEY2")
    elif flag == "num3":
        SERVICE_KEY = os.getenv("SERVICE_KEY3") 
    
    if not SERVICE_KEY:
        raise RuntimeError("환경변수 SERVICE_KEY가 없습니다. .env에 디코딩 키를 넣어주세요.")

    # 공공데이터 포털 호출용 공통 클라이언트 생성
    client = TourAPIClient(
        service_key_decoding=SERVICE_KEY,
        mobile_app="AppTest",
        base_url="https://apis.data.go.kr/B551011/KorService2",
    )
    
    # 데이터 폴더 준비
    ensure_data_dirs()

    print("⭐")
    # run_ldong_code(client)  # 법정동 데이터 API 호출
    # run_system_code(client) # 분류코드 데이터 API 호출
    code_df = base.main(write_to_disk=False)  # 코드테이블 구성 데이터를 전처리
    ingest_base_db.main(code_df=code_df)      # 전처리된 코드테이블 데이터를 DB에 적재
    # run_tourist_spot(client)  # 관광지 목록 API 호출
    # run_detailInfo(client)   # 관광지 상세정보 API 호출
    # run_detailIntro(client)  # 관광지 상세소개 API 호출
    ingest_tour_db.main(write_to_disk=False)  # 전처리된 관광지 데이터를 DB에 적재


if __name__ == "__main__":
    # flag = "num1"
    # flag = "num2"
    flag = "num3"

    main(flag)
