import datetime
import pandas as pd
import os
from django.conf import settings
from django.utils import timezone
from ..models import CurrentWeather, ShortForecast, MidForecast
from .weather_api import SEOUL_GU, get_current_weather, get_short_forecast, get_mid_forecast


class WeatherService:
    """날씨 데이터 수집 및 DB 저장 서비스"""
    
    # collect_and_save_weather_data 메서드 제거됨 - collect_save_and_load 사용
    
    @staticmethod
    def get_current_weather_summary():
        """현재 날씨 요약 정보 반환 (새로운 테이블 구조 사용)"""
        today = datetime.date.today().strftime("%Y%m%d")
        
        # 새로운 CurrentWeather 테이블에서 데이터 조회
        current_weather = CurrentWeather.objects.filter(
            date=today
        ).order_by('-time')
        
        weather_by_region = {}
        
        for weather in current_weather:
            region = weather.region
            
            # 각 구별로 가장 최근 데이터만 사용
            if region not in weather_by_region:
                weather_by_region[region] = {
                    '기온(℃)': str(weather.temperature) if weather.temperature is not None else '정보없음',
                    '습도(%)': str(weather.humidity) if weather.humidity is not None else '정보없음',
                    '풍속(m/s)': str(weather.wind_speed) if weather.wind_speed is not None else '정보없음',
                    '강수량(mm)': str(weather.rainfall) if weather.rainfall is not None else '0'
                }
        
        return weather_by_region
    
    # get_weather_forecast 메서드 제거됨 - 새로운 테이블 구조 사용
    
    @staticmethod
    def collect_and_save_to_csv():
        """API에서 날씨 데이터를 수집하고 CSV로 저장"""
        print("🌤️ 날씨 데이터 수집 및 CSV 저장 시작...")
        
        # API 데이터 폴더 경로
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        os.makedirs(api_data_dir, exist_ok=True)
        
        today = datetime.date.today().strftime("%Y%m%d")
        short_data = []
        
        # 1. 서울 구별 현재 날씨 + 단기예보 수집
        for gu, (nx, ny) in SEOUL_GU.items():
            print(f"📍 {gu} 데이터 수집 중...")
            
            # 현재 날씨
            current_data = get_current_weather(nx, ny)
            if current_data:
                for category, value in current_data.items():
                    short_data.append({
                        "지역": gu,
                        "타입": "현재",
                        "날짜": today,
                        "시간": datetime.datetime.now().strftime("%H%M"),
                        "항목": category,
                        "값": str(value)
                    })
            
            # 단기예보
            forecast_data = get_short_forecast(nx, ny)
            for forecast in forecast_data:
                short_data.append({
                    "지역": gu,
                    "타입": "단기",
                    "날짜": forecast["예보일자"],
                    "시간": forecast["예보시간"],
                    "항목": forecast["항목"],
                    "값": str(forecast["값"])
                })
        
        # 2. 서울 전체 중기예보 수집
        print("📍 서울 중기예보 수집 중...")
        mid_data = get_mid_forecast("11B10101")
        mid_formatted = []
        for mid_forecast in mid_data:
            mid_formatted.append({
                "지역": "서울",
                "타입": "중기",
                "날짜": mid_forecast["날짜"],
                "시간": mid_forecast["시간"],
                "항목": mid_forecast["항목"],
                "값": str(mid_forecast["값"])
            })
        
        # 3. CSV 파일로 저장
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        short_filename = os.path.join(api_data_dir, f"seoul_short_{timestamp}.csv")
        mid_filename = os.path.join(api_data_dir, f"seoul_mid_{timestamp}.csv")
        
        if short_data:
            pd.DataFrame(short_data).to_csv(short_filename, index=False, encoding="utf-8-sig")
            print(f"✅ 단기 데이터 CSV 저장: {short_filename}")
        
        if mid_formatted:
            pd.DataFrame(mid_formatted).to_csv(mid_filename, index=False, encoding="utf-8-sig")
            print(f"✅ 중기 데이터 CSV 저장: {mid_filename}")
        
        return {
            'short_file': short_filename if short_data else None,
            'mid_file': mid_filename if mid_formatted else None,
            'short_count': len(short_data),
            'mid_count': len(mid_formatted)
        }
    
    @staticmethod
    def load_csv_to_db(csv_file_path, replace_all=False):
        """CSV 파일을 읽어서 새로운 테이블 구조로 저장"""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_file_path}")
        
        print(f"📄 CSV 파일 로드 중: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        if df.empty:
            print("❌ CSV 파일이 비어있습니다.")
            return 0
        
        # 날짜별로 기존 데이터 삭제
        dates_in_csv = df['날짜'].unique()
        
        # 타입별로 데이터 분류 및 저장
        current_records = []
        short_records = []
        mid_records = []
        
        for _, row in df.iterrows():
            region = row['지역']
            weather_type = row['타입']
            date = str(row['날짜'])
            time = str(row['시간'])
            category = row['항목']
            value = str(row['값'])
            
            if weather_type == '현재':
                # 현재 날씨 데이터 처리
                WeatherService._process_current_weather(
                    current_records, region, date, time, category, value
                )
            elif weather_type == '단기':
                # 단기 예보 데이터 처리
                WeatherService._process_short_forecast(
                    short_records, region, date, time, category, value
                )
            elif weather_type == '중기':
                # 중기 예보 데이터 처리
                WeatherService._process_mid_forecast(
                    mid_records, region, date, time, category, value
                )
        
        total_saved = 0
        
        # 기존 데이터 삭제 및 새 데이터 저장
        if current_records:
            CurrentWeather.objects.filter(date__in=dates_in_csv).delete()
            CurrentWeather.objects.bulk_create(current_records, ignore_conflicts=True)
            total_saved += len(current_records)
            print(f"✅ 현재 날씨 저장: {len(current_records)}건")
        
        if short_records:
            ShortForecast.objects.filter(date__in=dates_in_csv).delete()
            ShortForecast.objects.bulk_create(short_records, ignore_conflicts=True)
            total_saved += len(short_records)
            print(f"✅ 단기 예보 저장: {len(short_records)}건")
        
        if mid_records:
            MidForecast.objects.filter(date__in=dates_in_csv).delete()
            MidForecast.objects.bulk_create(mid_records, ignore_conflicts=True)
            total_saved += len(mid_records)
            print(f"✅ 중기 예보 저장: {len(mid_records)}건")
        
        return total_saved
    
    @staticmethod
    def _process_current_weather(records, region, date, time, category, value):
        """현재 날씨 데이터 처리"""
        # 같은 지역, 날짜, 시간의 기존 레코드 찾기
        existing_record = None
        for record in records:
            if (record.region == region and record.date == date and record.time == time):
                existing_record = record
                break
        
        if not existing_record:
            existing_record = CurrentWeather(
                region=region,
                date=date,
                time=time
            )
            records.append(existing_record)
        
        # 카테고리별 값 설정
        try:
            if category == '기온(℃)':
                existing_record.temperature = float(value)
            elif category == '습도(%)':
                existing_record.humidity = int(value)
            elif category == '풍속(m/s)':
                existing_record.wind_speed = float(value)
            elif category == '강수량(mm)':
                existing_record.rainfall = float(value)
        except (ValueError, TypeError):
            print(f"⚠️ 값 변환 실패: {category} = {value}")
    
    @staticmethod
    def _process_short_forecast(records, region, date, forecast_time, category, value):
        """단기 예보 데이터 처리"""
        # 같은 지역, 날짜, 시간의 기존 레코드 찾기
        existing_record = None
        for record in records:
            if (record.region == region and record.date == date and record.forecast_time == forecast_time):
                existing_record = record
                break
        
        if not existing_record:
            existing_record = ShortForecast(
                region=region,
                date=date,
                forecast_time=forecast_time
            )
            records.append(existing_record)
        
        # 카테고리별 값 설정
        try:
            if category == 'TMP':
                existing_record.temperature = float(value)
            elif category == 'WSD':
                existing_record.wind_speed = float(value)
            elif category == 'PCP':
                existing_record.precipitation = value
        except (ValueError, TypeError):
            print(f"⚠️ 값 변환 실패: {category} = {value}")
    
    @staticmethod
    def _process_mid_forecast(records, region, date, period, category, value):
        """중기 예보 데이터 처리"""
        # 같은 지역, 날짜, 구간의 기존 레코드 찾기
        existing_record = None
        for record in records:
            if (record.region == region and record.date == date and record.period == period):
                existing_record = record
                break
        
        if not existing_record:
            existing_record = MidForecast(
                region=region,
                date=date,
                period=period
            )
            records.append(existing_record)
        
        # 카테고리별 값 설정
        try:
            if category == '날씨':
                existing_record.weather_condition = value
            elif category == '강수확률(%)':
                existing_record.rain_probability = int(value) if value != '-' else None
            elif category == '최저기온(℃)':
                existing_record.min_temperature = float(value) if value != '-' else None
            elif category == '최고기온(℃)':
                existing_record.max_temperature = float(value) if value != '-' else None
        except (ValueError, TypeError):
            print(f"⚠️ 값 변환 실패: {category} = {value}")
    
    @staticmethod
    def collect_save_and_load():
        """전체 파이프라인: API 수집 → CSV 저장 → DB 로드 → CSV 정리"""
        print("🚀 전체 날씨 데이터 파이프라인 시작...")
        
        # 1. 기존 CSV 파일들 정리 (1일 이상 된 파일)
        WeatherService.cleanup_old_csv_files(days=1)
        
        # 2. API 수집 및 CSV 저장
        csv_result = WeatherService.collect_and_save_to_csv()
        
        total_loaded = 0
        csv_files_to_delete = []
        
        # 3. 기존 전체 날씨 데이터 삭제 (새로운 테이블들)
        current_count = CurrentWeather.objects.all().count()
        short_count = ShortForecast.objects.all().count()
        mid_count = MidForecast.objects.all().count()
        
        CurrentWeather.objects.all().delete()
        ShortForecast.objects.all().delete()
        MidForecast.objects.all().delete()
        
        total_deleted = current_count + short_count + mid_count
        print(f"🗑️ 기존 전체 날씨 데이터 삭제 완료: {total_deleted}건 (현재:{current_count}, 단기:{short_count}, 중기:{mid_count})")
        
        # 4. CSV 파일들을 DB에 로드 (전체 교체 모드)
        if csv_result['short_file']:
            count = WeatherService.load_csv_to_db(csv_result['short_file'], replace_all=False)  # 이미 삭제했으므로 False
            total_loaded += count
            csv_files_to_delete.append(csv_result['short_file'])
        
        if csv_result['mid_file']:
            count = WeatherService.load_csv_to_db(csv_result['mid_file'], replace_all=False)  # 이미 삭제했으므로 False
            total_loaded += count
            csv_files_to_delete.append(csv_result['mid_file'])
        
        # 4. DB 로드 완료 후 CSV 파일 삭제 (선택사항)
        # WeatherService.delete_csv_files(csv_files_to_delete)
        
        print(f"🎉 파이프라인 완료! 총 {total_loaded}건 DB 저장")
        
        return {
            'csv_files': [csv_result['short_file'], csv_result['mid_file']],
            'total_records': total_loaded,
            'short_count': csv_result['short_count'],
            'mid_count': csv_result['mid_count']
        }
    
    @staticmethod
    def cleanup_old_csv_files(days=7):
        """오래된 CSV 파일들 정리"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        deleted_count = 0
        
        for filename in os.listdir(api_data_dir):
            if filename.endswith('.csv') and filename != '.gitkeep':
                file_path = os.path.join(api_data_dir, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"🗑️ 오래된 CSV 파일 삭제: {filename}")
                    except Exception as e:
                        print(f"❌ CSV 파일 삭제 실패: {filename} - {e}")
        
        if deleted_count > 0:
            print(f"✅ 총 {deleted_count}개의 오래된 CSV 파일을 정리했습니다.")
    
    @staticmethod
    def delete_csv_files(file_paths):
        """지정된 CSV 파일들 삭제"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"🗑️ CSV 파일 삭제: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"❌ CSV 파일 삭제 실패: {file_path} - {e}")
    
    @staticmethod
    def export_to_csv(filename=None):
        """새로운 테이블 구조의 날씨 데이터를 CSV로 내보내기"""
        if filename is None:
            api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
            os.makedirs(api_data_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(api_data_dir, f"weather_export_{timestamp}.csv")
        
        # 새로운 테이블들에서 데이터 수집
        export_data = []
        
        # 현재 날씨
        for weather in CurrentWeather.objects.all():
            export_data.append({
                '지역': weather.region,
                '타입': '현재',
                '날짜': weather.date,
                '시간': weather.time,
                '온도': weather.temperature,
                '습도': weather.humidity,
                '풍속': weather.wind_speed,
                '강수량': weather.rainfall,
                '생성일시': weather.created_at
            })
        
        # 단기 예보
        for forecast in ShortForecast.objects.all():
            export_data.append({
                '지역': forecast.region,
                '타입': '단기',
                '날짜': forecast.date,
                '시간': forecast.forecast_time,
                '온도': forecast.temperature,
                '풍속': forecast.wind_speed,
                '강수량': forecast.precipitation,
                '생성일시': forecast.created_at
            })
        
        # 중기 예보
        for forecast in MidForecast.objects.all():
            export_data.append({
                '지역': forecast.region,
                '타입': '중기',
                '날짜': forecast.date,
                '구간': forecast.period,
                '날씨상태': forecast.weather_condition,
                '강수확률': forecast.rain_probability,
                '최저기온': forecast.min_temperature,
                '최고기온': forecast.max_temperature,
                '생성일시': forecast.created_at
            })
        
        df = pd.DataFrame(export_data)
        if not df.empty:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ CSV 내보내기 완료: {filename} ({len(export_data)}건)")
        
        return filename