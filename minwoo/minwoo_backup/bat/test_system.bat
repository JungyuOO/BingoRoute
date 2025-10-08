@echo off
echo ========================================
echo 🚀 BINGOROUTE 프로젝트 테스트 시작
echo ========================================

echo.
echo 📋 1. Docker 컨테이너 상태 확인
docker ps

echo.
echo 📋 2. 백엔드 API 테스트
echo 현재 날씨 API 테스트...
docker exec -it bingoroute_backend python manage.py shell -c "import requests; print('현재 날씨 API:', requests.get('http://localhost:8000/api/weather/current/').status_code)"

echo 중기 예보 API 테스트...
docker exec -it bingoroute_backend python manage.py shell -c "import requests; print('중기 예보 API:', requests.get('http://localhost:8000/api/weather/mid-forecast/').status_code)"

echo 통계 API 테스트...
docker exec -it bingoroute_backend python manage.py shell -c "import requests; print('통계 API:', requests.get('http://localhost:8000/api/weather/statistics/').status_code)"

echo.
echo 📋 3. 데이터베이스 상태 확인
docker exec -it bingoroute_backend python manage.py shell -c "from destinations.models import CurrentWeather, ShortForecast, MidForecast; print('현재 날씨:', CurrentWeather.objects.count(), '건'); print('단기 예보:', ShortForecast.objects.count(), '건'); print('중기 예보:', MidForecast.objects.count(), '건')"

echo.
echo 📋 4. 프론트엔드 서버 시작
echo React 개발 서버를 시작합니다...
cd web/react-app
start cmd /k "npm run dev"

echo.
echo ========================================
echo ✅ 테스트 완료!
echo ========================================
echo.
echo 🌐 접속 URL:
echo   - React 앱: http://localhost:5173/
echo   - Django API: http://localhost:8000/
echo   - Django Admin: http://localhost:8000/admin/
echo.
echo 🎯 테스트할 주요 기능:
echo   1. 메인 페이지에서 실시간 날씨 확인
echo   2. 여행 계획 페이지에서 날씨 기반 추천 체험
echo   3. 마이페이지에서 저장된 계획 확인
echo.
pause