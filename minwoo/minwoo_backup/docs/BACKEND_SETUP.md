# 🚀 BINGOROUTE 백엔드 설정 가이드

## 📋 사전 요구사항
- Docker & Docker Compose 설치됨
- Git 설치됨

## 🔧 설정 단계

### 1. 코드 받기
```bash
# 저장소 클론 (처음인 경우)
git clone [저장소URL]
cd BINGOROUTE

# 또는 기존 저장소에서 브랜치 받기
git fetch origin
git checkout [브랜치명]
git pull origin [브랜치명]
```

### 2. 자동 설정 (추천)
```bash
# Windows
setup_backend.bat

# 또는 수동 설정 계속 진행
```

### 3. 수동 설정

#### 3-1. Docker 컨테이너 실행
```bash
docker-compose up -d
```

#### 3-2. 데이터베이스 마이그레이션
```bash
docker exec -it bingoroute_backend python manage.py migrate
```

#### 3-3. 초기 데이터 로드
```bash
docker exec -it bingoroute_backend python load_initial_data.py
```

#### 3-4. 날씨 데이터 수집
```bash
docker exec -it bingoroute_backend python manage.py collect_weather
```

## ✅ 설정 완료 확인

### 컨테이너 상태 확인
```bash
docker ps
```
다음 2개 컨테이너가 실행 중이어야 합니다:
- `bingoroute_backend` (포트 8000)
- `bingoroute_mysql` (포트 3306)

### API 테스트
브라우저에서 다음 URL들을 확인:
- http://localhost:8000/api/weather/current/
- http://localhost:8000/api/weather/statistics/

### 데이터 확인
```bash
docker exec -it bingoroute_backend python manage.py shell -c "
from destinations.models import CurrentWeather, ShortForecast, MidForecast
print('현재 날씨:', CurrentWeather.objects.count(), '건')
print('단기 예보:', ShortForecast.objects.count(), '건')
print('중기 예보:', MidForecast.objects.count(), '건')
"
```

## 🌐 접속 정보
- **Django API**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **MySQL**: localhost:3306

## 🔄 일상적인 사용

### 날씨 데이터 업데이트
```bash
docker exec -it bingoroute_backend python manage.py collect_weather
```

### 컨테이너 재시작
```bash
docker-compose restart
```

### 컨테이너 중지
```bash
docker-compose down
```

### 로그 확인
```bash
# 백엔드 로그
docker logs bingoroute_backend

# MySQL 로그
docker logs bingoroute_mysql
```

## 🐛 문제 해결

### 포트 충돌 시
```bash
# 사용 중인 포트 확인
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# 프로세스 종료 후 재시작
docker-compose down
docker-compose up -d
```

### 데이터베이스 초기화가 필요한 경우
```bash
docker-compose down
docker volume rm bingoroute_mysql_data
docker-compose up -d
# 그 후 3-2부터 다시 실행
```

### 컨테이너 재빌드
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 주요 API 엔드포인트
- `GET /api/weather/current/` - 서울 25개 구 현재 날씨
- `GET /api/weather/mid-forecast/` - 중기 예보 (10일)
- `GET /api/weather/statistics/` - 날씨 데이터 통계
- `GET /api/destinations/` - 여행지 목록

### 👤 인증 API (JWT Access 토큰)
- `POST /api/auth/signup/`
  - body: `{ "name": string, "email": string, "password": string, "confirm_password": string }`
  - response: `{ user: {...} }` (필요 시 토큰 발급 로직 추가 가능)
- `POST /api/auth/login/`
  - body: `{ "email": string, "password": string }`
  - response: `{ access: string, user: {...} }`

사용법
- 요청 시 `Authorization: Bearer <access_token>` 헤더로 인증합니다.
- 세션/쿠키/CSRF는 사용하지 않습니다. CORS는 기본 허용(origin 화이트리스트 포함).

## 🎯 프론트엔드 연동
백엔드가 정상 실행되면 React 앱에서 다음과 같이 연동:
```javascript
// React 앱에서 API 호출
const response = await fetch('http://localhost:8000/api/weather/current/');
const data = await response.json();
```
