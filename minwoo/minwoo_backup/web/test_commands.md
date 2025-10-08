# 🧪 BINGOROUTE 테스트 명령어 모음

## 백엔드 테스트

### Docker 컨테이너 관리
```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 상태 확인
docker ps

# 컨테이너 재시작
docker-compose restart backend

# 컨테이너 중지
docker-compose down
```

### API 테스트
```bash
# 현재 날씨 API 테스트
docker exec -it bingoroute_backend python manage.py shell -c "
import requests
response = requests.get('http://localhost:8000/api/weather/current/')
print('Status:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('구 개수:', len(data['data']))
"

# 중기 예보 API 테스트
docker exec -it bingoroute_backend python manage.py shell -c "
import requests
response = requests.get('http://localhost:8000/api/weather/mid-forecast/')
print('중기 예보 API:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('예보 데이터:', len(data['data']), '건')
"

# 통계 API 테스트
docker exec -it bingoroute_backend python manage.py shell -c "
import requests
response = requests.get('http://localhost:8000/api/weather/statistics/')
print('통계 API:', response.status_code)
if response.status_code == 200:
    stats = response.json()['data']
    print('현재 날씨:', stats['current_weather'])
    print('단기 예보:', stats['short_forecast'])
    print('중기 예보:', stats['mid_forecast'])
    print('총 데이터:', stats['total'])
"
```

### 데이터베이스 테스트
```bash
# 테이블 데이터 개수 확인
docker exec -it bingoroute_backend python manage.py shell -c "
from destinations.models import CurrentWeather, ShortForecast, MidForecast
print('=== 데이터베이스 현황 ===')
print('현재 날씨:', CurrentWeather.objects.count(), '건')
print('단기 예보:', ShortForecast.objects.count(), '건')
print('중기 예보:', MidForecast.objects.count(), '건')
"

# 샘플 데이터 확인
docker exec -it bingoroute_backend python manage.py shell -c "
from destinations.models import CurrentWeather
print('=== 현재 날씨 샘플 ===')
for weather in CurrentWeather.objects.all()[:5]:
    print(f'{weather.region}: {weather.temperature}°C, 습도 {weather.humidity}%')
"
```

### 날씨 데이터 수집
```bash
# 새로운 날씨 데이터 수집
docker exec -it bingoroute_backend python manage.py collect_weather
```

## 프론트엔드 테스트

### React 개발 서버
```bash
# React 앱 디렉토리로 이동
cd web/react-app

# 개발 서버 시작
npm run dev

# 의존성 설치 (필요시)
npm install

# 빌드 테스트
npm run build
```

### 브라우저 테스트
```bash
# 기본 브라우저에서 열기 (Windows)
start http://localhost:5173/

# 특정 브라우저에서 열기
start chrome http://localhost:5173/
start firefox http://localhost:5173/
```

## 통합 테스트

### 전체 시스템 상태 확인
```bash
# 모든 서비스 상태 한번에 확인
docker exec -it bingoroute_backend python manage.py shell -c "
import requests
from destinations.models import CurrentWeather, ShortForecast, MidForecast

print('=== 시스템 상태 ===')
print('DB - 현재 날씨:', CurrentWeather.objects.count())
print('DB - 단기 예보:', ShortForecast.objects.count())
print('DB - 중기 예보:', MidForecast.objects.count())

print('API - 현재 날씨:', requests.get('http://localhost:8000/api/weather/current/').status_code)
print('API - 중기 예보:', requests.get('http://localhost:8000/api/weather/mid-forecast/').status_code)
print('API - 통계:', requests.get('http://localhost:8000/api/weather/statistics/').status_code)
print('✅ 모든 시스템 정상!')
"
```

## 주요 테스트 시나리오

### 1. 메인 페이지 테스트
- http://localhost:5173/ 접속
- 실시간 날씨 정보 표시 확인
- 구별 선택 드롭다운 테스트
- 온도, 습도, 풍속 데이터 확인

### 2. AI 여행 플래너(챗봇) 테스트
- http://localhost:5173/planner 접속
- 초기 환영 메시지와 추천 칩 노출 확인
- 칩 선택 또는 메시지 입력으로 대화 진행
- 답변 표시와 입력/전송 동작 확인

### 3. 마이페이지 테스트
- http://localhost:5173/mypage 접속
- 저장된 여행 계획 목록 확인
- 날씨 점수 표시 확인
- 계획 상세 정보 확인

### 4. API 직접 테스트
- http://localhost:8000/api/weather/current/
- http://localhost:8000/api/weather/mid-forecast/
- http://localhost:8000/api/weather/statistics/

## 문제 해결

### 포트 충돌 시
```bash
# 사용 중인 포트 확인
netstat -ano | findstr :5173
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# 프로세스 종료 (PID 확인 후)
taskkill /PID [PID번호] /F
```

### 컨테이너 문제 시
```bash
# 컨테이너 로그 확인
docker logs bingoroute_backend
docker logs bingoroute_mysql

# 컨테이너 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### React 앱 문제 시
```bash
# 캐시 정리
npm run dev -- --force

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```
