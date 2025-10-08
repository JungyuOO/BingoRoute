@echo off
echo ========================================
echo 🚀 BINGOROUTE 백엔드 초기 설정
echo ========================================

echo.
echo 1. Docker 컨테이너 시작...
docker-compose up -d

echo.
echo 2. 3초 대기 (MySQL 준비 시간)...
timeout /t 3 /nobreak > nul

echo.
echo 3. 데이터베이스 마이그레이션...
docker exec -it bingoroute_backend python manage.py migrate

echo.
echo 4. 초기 데이터 로드...
docker exec -it bingoroute_backend python load_initial_data.py

echo.
echo 5. 날씨 데이터 수집...
docker exec -it bingoroute_backend python manage.py collect_weather

echo.
echo 6. 상태 확인...
docker ps

echo.
echo ========================================
echo ✅ 백엔드 설정 완료!
echo ========================================
echo.
echo 🌐 접속 URL:
echo   - Django API: http://localhost:8000/
echo   - Django Admin: http://localhost:8000/admin/
echo.
echo 🧪 API 테스트:
echo   - 현재 날씨: http://localhost:8000/api/weather/current/
echo   - 중기 예보: http://localhost:8000/api/weather/mid-forecast/
echo   - 통계: http://localhost:8000/api/weather/statistics/
echo.
pause