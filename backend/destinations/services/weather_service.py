import datetime
import pandas as pd
import os
from django.conf import settings
from .weather_api import SEOUL_GU, get_current_weather, get_short_forecast, get_mid_forecast


class WeatherService:
    """날씨 데이터 수집 및 CSV 저장/조회 서비스"""

    @staticmethod
    def get_current_weather_summary():
        """api_data의 최신 단기 예보 CSV에서 서울 현재 요약 정보를 반환"""
        try:
            csv_file = WeatherService._get_latest_weather_csv()
            if not csv_file or not os.path.exists(csv_file):
                return { 'summary': '날씨 데이터 파일이 없습니다.' }

            # CSV는 한글 헤더 + BOM 가능성 → utf-8-sig로 로드
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            required_cols = {'지역', '타입', '날짜', '시간', '항목', '값'}
            if not required_cols.issubset(set(df.columns)):
                return { 'summary': '날씨 CSV 형식이 예상과 다릅니다.' }

            # KST 기준 현재 날짜/시간
            import pytz
            seoul_tz = pytz.timezone('Asia/Seoul')
            now_seoul = datetime.datetime.now(seoul_tz)
            today = now_seoul.strftime('%Y%m%d')
            current_hhmm = int(now_seoul.strftime('%H%M'))

            # 문자열 정규화
            df['날짜'] = df['날짜'].astype(str)
            df['시간'] = df['시간'].astype(int)

            # 오늘 데이터 중 현재 시각 이전(포함) 가장 가까운 값을 사용
            df_today = df[df['날짜'] == today]
            if df_today.empty:
                # 오늘 데이터가 없으면 최신 날짜 사용
                latest_day = df['날짜'].astype(str).max()
                df_today = df[df['날짜'].astype(str) == latest_day]

            df_today = df_today[df_today['시간'] <= current_hhmm]
            if df_today.empty:
                # 자정 직후 같은 경우: 가장 이른 시각 사용
                min_time = df[df['날짜'] == df_today['날짜'].iloc[0] if not df_today.empty else df['날짜'].max()]['시간'].min()
                df_today = df[df['시간'] == min_time]

            # 지역·항목별 최근 시각 값만 추출
            df_today = df_today.sort_values(['지역', '시간'])
            latest = df_today.groupby(['지역', '항목']).tail(1)
            pivot = latest.pivot(index='지역', columns='항목', values='값')

            # 수치 변환 및 요약
            def to_float(val):
                try:
                    return float(str(val).replace('mm', '').replace('cm', ''))
                except Exception:
                    return None

            tmp = pivot.get('TMP')
            wsd = pivot.get('WSD')
            pcp = pivot.get('PCP')  # 강수없음/수치(mm)

            mean_tmp = float(tmp.astype(float).mean()) if tmp is not None else None
            mean_wsd = float(wsd.astype(float).mean()) if wsd is not None else None

            any_rain = False
            if pcp is not None:
                any_rain = pcp.apply(lambda v: str(v).strip() not in ['강수없음', '0', '0mm', '0.0']).any()

            closest_time = int(df_today['시간'].max()) if not df_today.empty else current_hhmm
            closest_time_str = f"{closest_time:04d}"

            parts = []
            if mean_tmp is not None:
                parts.append(f"기온 {mean_tmp:.1f}℃")
            if mean_wsd is not None:
                parts.append(f"풍속 {mean_wsd:.1f} m/s")
            parts.append('강수 중' if any_rain else '강수 없음')
            summary = f"현재 서울 {parts[0]}" if parts else "현재 날씨 정보를 불러오지 못했습니다."
            if len(parts) > 1:
                summary += f", {', '.join(parts[1:])}"
            summary += f" (기준 {today} {closest_time_str})"

            # 상세 지역 데이터도 포함(선택)
            regions = []
            for region in pivot.index:
                regions.append({
                    'region': region,
                    'TMP': float(pivot.at[region, 'TMP']) if 'TMP' in pivot.columns and pd.notna(pivot.at[region, 'TMP']) else None,
                    'WSD': float(pivot.at[region, 'WSD']) if 'WSD' in pivot.columns and pd.notna(pivot.at[region, 'WSD']) else None,
                    'PCP': pivot.at[region, 'PCP'] if 'PCP' in pivot.columns and pd.notna(pivot.at[region, 'PCP']) else None,
                })

            return {
                'summary': summary,
                'temperature': round(mean_tmp, 1) if mean_tmp is not None else None,
                'windSpeed': round(mean_wsd, 1) if mean_wsd is not None else None,
                'precipitation': '강수' if any_rain else '없음',
                'time': f"{today}{closest_time_str}",
                'regions': regions,
            }

        except Exception as e:
            print(f"❌ 현재 날씨 조회 오류: {e}")
            return { 'summary': '현재 날씨 정보를 불러오지 못했습니다.' }
    
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
        return # 추후 주석처리 원복할 때 삭제 예정 
        
        # cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        # deleted_count = 0
        #
        # for filename in os.listdir(api_data_dir):
            # if filename.endswith('.csv') and filename != '.gitkeep':
                # file_path = os.path.join(api_data_dir, filename)
                # file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                #
                # if file_time < cutoff_time:
                    # try:
                        # os.remove(file_path)
                        # deleted_count += 1
                        # print(f"🗑️ 오래된 CSV 파일 삭제: {filename}")
                    # except Exception as e:
                        # print(f"❌ CSV 파일 삭제 실패: {filename} - {e}")
        #
        # if deleted_count > 0:
            # print(f"✅ 총 {deleted_count}개의 오래된 CSV 파일을 정리했습니다.")
    
    @staticmethod
    def delete_csv_files(file_paths):
        """지정된 CSV 파일들 삭제"""
        return # 추후 주석처리 원복할 때 삭제 예정 
        # for file_path in file_paths:
            # if file_path and os.path.exists(file_path):
                # try:
                    # os.remove(file_path)
                    # print(f"🗑️ CSV 파일 삭제: {os.path.basename(file_path)}")
                # except Exception as e:
                    # print(f"❌ CSV 파일 삭제 실패: {file_path} - {e}")
    #

    
    @staticmethod
    def _get_latest_weather_csv():
        """가장 최신의 단기예보(seoul_short_*.csv) 파일 경로 반환"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return None
        candidates = [
            os.path.join(api_data_dir, f)
            for f in os.listdir(api_data_dir)
            if f.startswith('seoul_short_') and f.endswith('.csv')
        ]
        if not candidates:
            return None
        # 파일명 또는 생성시간 기준 최신 선택
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return candidates[0]
    
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
