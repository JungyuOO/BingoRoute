import datetime
import pandas as pd
import os
from django.conf import settings
from .weather_api import SEOUL_GU, get_current_weather, get_short_forecast, get_mid_forecast


class WeatherService:
    """날씨 데이터 수집 및 CSV 저장/조회 서비스"""
    # NOTE:
    # 프로젝트 요구에 따라 api_data 폴더의 CSV 더미 데이터 사용을 잠정 중단합니다.
    # 아래 메서드들에서 CSV 파일을 읽거나 쓰는 부분을 안전하게 우회하고,
    # 추후 실제 API 연동 시 주석을 원복하거나 API 결과를 직접 반환하도록 교체하세요.

    # collect_and_save_weather_data 메서드 제거됨 - collect_save_and_load 사용

    @staticmethod
    def get_current_weather_summary():
        """현재 시간대 날씨 정보 반환 (단기 예보에서 현재 시간대 데이터 추출)"""
        try:
            # CSV 더미 데이터 사용 중단: 빈 결과 반환 (API 직결 예정)
            # 기존 CSV 경로 탐색/로드 로직은 보존하되 비활성화합니다.
            # csv_file = WeatherService._get_latest_weather_csv()
            # if not csv_file:
            #     WeatherService.collect_and_save_to_csv()
            #     csv_file = WeatherService._get_latest_weather_csv()
            # if not csv_file:
            #     return {}
            # df = pd.read_csv(csv_file)
            return {}

            # 서울 시간대 기준으로 현재 시간 계산
            import pytz
            seoul_tz = pytz.timezone('Asia/Seoul')
            now_seoul = datetime.datetime.now(seoul_tz)
            today = now_seoul.strftime("%Y%m%d")
            current_hour = now_seoul.hour

            # 현재 시간에 가장 가까운 예보 시간 찾기 (3시간 간격)
            forecast_hours = [0, 3, 6, 9, 12, 15, 18, 21]

            # 현재 시간 이하 중 가장 가까운 값 우선
            past_hours = [h for h in forecast_hours if h <= current_hour]
            if past_hours:
                closest_hour = max(past_hours)
            else:
                closest_hour = min(forecast_hours)  # 자정 직후 같은 경우
            target_time = f"{closest_hour:02d}00"

            # 기존 CSV 기반 가공 로직 주석화 (위에서 빈 dict 반환)
            # return weather_by_region

        except Exception as e:
            print(f"❌ 현재 날씨 조회 오류: {e}")
            return {}

    @staticmethod
    def get_weather_forecast(region=None, days=3):
        """날씨 예보 조회 (CSV에서 읽기)"""
        try:
            # CSV 더미 데이터 사용 중단: 빈 리스트 반환 (API 직결 예정)
            return []

        except Exception as e:
            print(f"❌ 날씨 예보 조회 오류: {e}")
            return []

    @staticmethod
    def collect_and_save_to_csv():
        """API에서 날씨 데이터를 수집하고 CSV로 저장"""
        # CSV 더미 데이터 저장 비활성화
        # 추후 실제 API 연동 시, CSV 저장 없이 메모리/DB 저장으로 교체 가능
        print("🌤️ (비활성화) CSV 저장 로직 우회: 더미 파일을 생성하지 않습니다.")
        return {
            'short_file': None,
            'mid_file': None,
            'short_count': 0,
            'mid_count': 0
        }

    @staticmethod
    def cleanup_old_csv_files(days=7):
        """오래된 CSV 파일들 정리"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return
        return  # 추후 주석처리 원복할 때 삭제 예정

        # cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        # deleted_count = 0
        #
        # for filename in os.listdir(api_data_dir):
        #     if filename.endswith('.csv') and filename != '.gitkeep':
        #         file_path = os.path.join(api_data_dir, filename)
        #         file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        #
        #         if file_time < cutoff_time:
        #             try:
        #                 os.remove(file_path)
        #                 deleted_count += 1
        #                 print(f"🗑️ 오래된 CSV 파일 삭제: {filename}")
        #             except Exception as e:
        #                 print(f"❌ CSV 파일 삭제 실패: {filename} - {e}")
        #
        # if deleted_count > 0:
        #     print(f"✅ 총 {deleted_count}개의 오래된 CSV 파일을 정리했습니다.")

    @staticmethod
    def delete_csv_files(file_paths):
        """지정된 CSV 파일들 삭제"""
        return  # 추후 주석처리 원복할 때 삭제 예정
        # for file_path in file_paths:
        #     if file_path and os.path.exists(file_path):
        #         try:
        #             os.remove(file_path)
        #             print(f"🗑️ CSV 파일 삭제: {os.path.basename(file_path)}")
        #         except Exception as e:
        #             print(f"❌ CSV 파일 삭제 실패: {file_path} - {e}")
    #

    @staticmethod
    def _get_latest_weather_csv():
        """가장 최신의 날씨 CSV 파일 경로 반환"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return None
        # CSV 더미 데이터 탐색 비활성화
        return None

    @staticmethod
    def get_mid_forecast_for_algorithm():
        """추천 알고리즘용 중기예보 데이터 조회 (CSV에서 읽기)"""
        try:
            # CSV 더미 데이터 사용 중단: 빈 리스트 반환 (API 직결 예정)
            return []

        except Exception as e:
            print(f"❌ 중기예보 조회 오류: {e}")
            return []

    @staticmethod
    def _get_latest_mid_csv():
        """가장 최신의 중기예보 CSV 파일 경로 반환"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return None
        # CSV 더미 데이터 탐색 비활성화
        return None

    @staticmethod
    def get_weather_statistics():
        """날씨 데이터 통계 조회 (CSV 기반)"""
        try:
            # CSV 더미 데이터 통계 비활성화: 0으로 반환
            return {
                'short_forecast': 0,
                'mid_forecast': 0,
                'legacy_data': 0,
                'total': 0
            }

        except Exception as e:
            print(f"❌ 통계 조회 오류: {e}")
            return {
                'short_forecast': 0,
                'mid_forecast': 0,
                'legacy_data': 0,
                'total': 0
            }

    @staticmethod
    def get_weather_by_time(target_date=None, target_time=None):
        """특정 시간대의 서울 구별 날씨 조회"""
        try:
            # CSV 더미 데이터 사용 중단: 빈 리스트 반환 (API 직결 예정)
            return []

            # 서울 시간대 기준으로 기본값 설정
            import pytz
            seoul_tz = pytz.timezone('Asia/Seoul')
            now_seoul = datetime.datetime.now(seoul_tz)

            if not target_date:
                target_date = now_seoul.strftime("%Y%m%d")

            if not target_time:
                current_hour = now_seoul.hour
                # 3시간 간격으로 가장 가까운 시간 찾기
                forecast_hours = [0, 3, 6, 9, 12, 15, 18, 21]
                closest_hour = min(forecast_hours, key=lambda x: abs(x - current_hour))
                target_time = f"{closest_hour:02d}00"

            # 기존 CSV 기반 가공 로직 주석화 (위에서 빈 리스트 반환)
            # return list(weather_by_region.values())

        except Exception as e:
            print(f"❌ 시간대별 날씨 조회 오류: {e}")
            return []

    @staticmethod
    def _format_date(date_string):
        """날짜 포맷팅 유틸리티"""
        if not date_string or len(date_string) != 8:
            return date_string

        year = date_string[:4]
        month = date_string[4:6]
        day = date_string[6:8]

        today = datetime.date.today()
        target_date = datetime.date(int(year), int(month), int(day))

        if target_date == today:
            return '오늘'
        elif target_date == today + datetime.timedelta(days=1):
            return '내일'
        else:
            return f"{month}/{day}"
