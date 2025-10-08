@echo off
echo 🗑️ CSV 파일 정리 도구

echo.
echo 선택하세요:
echo 1. 7일 이상 된 파일만 삭제 (기본)
echo 2. 1일 이상 된 파일 삭제
echo 3. 모든 CSV 파일 삭제
echo 4. 현재 CSV 파일 목록 확인
echo.

set /p choice="선택 (1-4): "

if "%choice%"=="1" (
    echo 7일 이상 된 CSV 파일을 삭제합니다...
    docker exec -it bingoroute_backend python manage.py shell -c "from destinations.services.weather_service import WeatherService; WeatherService.cleanup_old_csv_files(days=7)"
) else if "%choice%"=="2" (
    echo 1일 이상 된 CSV 파일을 삭제합니다...
    docker exec -it bingoroute_backend python manage.py shell -c "from destinations.services.weather_service import WeatherService; WeatherService.cleanup_old_csv_files(days=1)"
) else if "%choice%"=="3" (
    echo 모든 CSV 파일을 삭제합니다...
    docker exec -it bingoroute_backend python manage.py shell -c "from destinations.services.weather_service import WeatherService; WeatherService.cleanup_old_csv_files(days=0)"
) else if "%choice%"=="4" (
    echo 현재 CSV 파일 목록:
    docker exec -it bingoroute_backend ls -la /app/api_data/
) else (
    echo 잘못된 선택입니다.
)

echo.
pause