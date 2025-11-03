from django.apps import AppConfig
import threading
import os
import datetime


class TouristConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service'

    def ready(self):
        """Django 앱이 시작될 때 실행되는 초기화 메서드"""
        if hasattr(self, '_weather_collection_started'):
            return
        self._weather_collection_started = True
        self._start_weather_collection()

    def _start_weather_collection(self):
        """백그라운드에서 날씨 데이터 수집 시작"""

        def collect_weather():
            try:
                from .weather_service import WeatherService
                print("🌤️ Django 시작 시 날씨 데이터 자동 수집 확인...")

                latest_csv = WeatherService._get_latest_weather_csv()
                should_collect = False

                if not latest_csv:
                    print("📄 기존 날씨 CSV 파일이 없습니다.")
                    should_collect = True
                else:
                    file_time = datetime.datetime.fromtimestamp(os.path.getctime(latest_csv))
                    now = datetime.datetime.now()
                    time_diff = now - file_time

                    if time_diff.total_seconds() > 3 * 3600:
                        print(f"📄 기존 CSV 파일이 {time_diff}만큼 오래되었습니다. 새로 수집합니다.")
                        should_collect = True
                    else:
                        print(f"✅ 최신 날씨 CSV 파일 발견 ({time_diff} 전), 수집 생략")

                if should_collect:
                    result = WeatherService.collect_and_save_to_csv()
                    print(f"✅ 날씨 데이터 자동 수집 완료! 단기:{result['short_count']}건, 중기:{result['mid_count']}건")

            except Exception as e:
                print(f"❌ 날씨 데이터 자동 수집 실패: {e}")

        thread = threading.Thread(target=collect_weather, daemon=True)
        thread.start()
