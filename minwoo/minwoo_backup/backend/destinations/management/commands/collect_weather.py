from django.core.management.base import BaseCommand
from destinations.services.weather_service import WeatherService


class Command(BaseCommand):
    help = '날씨 API에서 데이터를 수집하여 CSV 저장 후 DB에 로드합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-only',
            action='store_true',
            help='CSV 파일만 생성하고 DB에는 저장하지 않음',
        )
        parser.add_argument(
            '--load-csv',
            type=str,
            help='지정된 CSV 파일을 DB에 로드',
        )
        parser.add_argument(
            '--export-db',
            action='store_true',
            help='DB 데이터를 CSV로 내보내기',
        )
        parser.add_argument(
            '--cleanup-csv',
            action='store_true',
            help='오래된 CSV 파일들 정리',
        )
        parser.add_argument(
            '--delete-after-load',
            action='store_true',
            help='DB 로드 후 CSV 파일 삭제',
        )
        parser.add_argument(
            '--replace-all',
            action='store_true',
            help='기존 모든 날씨 데이터를 삭제하고 새 데이터로 교체',
        )

    def handle(self, *args, **options):
        try:
            if options['load_csv']:
                # 특정 CSV 파일을 DB에 로드
                csv_file = options['load_csv']
                replace_all = options.get('replace_all', False)
                self.stdout.write(f'📄 CSV 파일 로드: {csv_file}')
                if replace_all:
                    self.stdout.write('🗑️ 기존 모든 데이터를 삭제하고 새 데이터로 교체합니다.')
                count = WeatherService.load_csv_to_db(csv_file, replace_all=replace_all)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {count}건의 데이터를 DB에 저장했습니다.')
                )
                
            elif options['export_db']:
                # DB 데이터를 CSV로 내보내기
                self.stdout.write('📤 DB 데이터를 CSV로 내보내는 중...')
                filename = WeatherService.export_to_csv()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ CSV 파일 생성: {filename}')
                )
                
            elif options['cleanup_csv']:
                # 오래된 CSV 파일들 정리
                self.stdout.write('🗑️ 오래된 CSV 파일들을 정리하는 중...')
                WeatherService.cleanup_old_csv_files()
                self.stdout.write(
                    self.style.SUCCESS('✅ CSV 파일 정리 완료')
                )
                
            elif options['csv_only']:
                # CSV 파일만 생성
                self.stdout.write('🌤️ 날씨 데이터 수집 및 CSV 저장 중...')
                result = WeatherService.collect_and_save_to_csv()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ CSV 파일 생성 완료:')
                )
                if result['short_file']:
                    self.stdout.write(f'  - 단기: {result["short_file"]} ({result["short_count"]}건)')
                if result['mid_file']:
                    self.stdout.write(f'  - 중기: {result["mid_file"]} ({result["mid_count"]}건)')
                    
            else:
                # 전체 파이프라인 실행 (기본)
                self.stdout.write(
                    self.style.SUCCESS('🚀 전체 날씨 데이터 파이프라인을 시작합니다...')
                )
                result = WeatherService.collect_save_and_load()
                
                self.stdout.write(
                    self.style.SUCCESS(f'🎉 파이프라인 완료!')
                )
                self.stdout.write(f'  - 총 DB 저장: {result["total_records"]}건')
                self.stdout.write(f'  - 단기 데이터: {result["short_count"]}건')
                self.stdout.write(f'  - 중기 데이터: {result["mid_count"]}건')
                for csv_file in result['csv_files']:
                    if csv_file:
                        self.stdout.write(f'  - CSV: {csv_file}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 오류 발생: {str(e)}')
            )