@echo off
echo 🚀 BINGOROUTE 빠른 시작

echo 1. Docker 컨테이너 시작...
docker-compose up -d

echo 2. 3초 대기 (서버 준비 시간)...
timeout /t 3 /nobreak > nul

echo 3. React 개발 서버 시작...
cd web/react-app
start cmd /k "npm run dev"

echo 4. 브라우저에서 앱 열기...
timeout /t 2 /nobreak > nul
start http://localhost:5173/

echo ✅ 시작 완료!
echo React 앱: http://localhost:5173/
echo Django API: http://localhost:8000/
pause