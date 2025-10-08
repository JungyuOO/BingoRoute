# 🔧 BINGOROUTE Backend (Django)

## 📋 프로젝트 개요
- **프레임워크**: Django 4.2.7
- **데이터베이스**: MySQL 8.0
- **API**: Django REST Framework
- **컨테이너**: Docker & Docker Compose
- **개발 서버**: http://localhost:8000/

## 📁 프로젝트 구조

```
backend/
├── bingoroute_api/            # Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py            # Django 설정 파일
│   ├── urls.py                # 메인 URL 라우팅
│   ├── wsgi.py                # WSGI 설정
│   └── asgi.py                # ASGI 설정
├── destinations/              # 메인 앱
│   ├── migrations/            # 데이터베이스 마이그레이션
│   │   ├── 0001_initial.py        # 초기 모델 생성
│   │   ├── 0002_weather_models.py # 날씨 모델 추가
│   │   └── 0003_remove_weatherdata.py # 구버전 모델 제거
│   ├── management/            # Django 관리 명령어
│   │   └── commands/
│   │       └── collect_weather.py # 날씨 데이터 수집 명령어
│   ├── services/              # 비즈니스 로직 서비스
│   │   ├── weather_api.py         # 기상청 API 연동
│   │   └── weather_service.py     # 날씨 데이터 처리 서비스
│   ├── fixtures/              # 초기 데이터
│   │   └── destinations.json      # 여행지 초기 데이터
│   ├── __init__.py
│   ├── admin.py               # Django 관리자 설정
│   ├── apps.py                # 앱 설정
│   ├── models.py              # 데이터베이스 모델
│   ├── serializers.py         # DRF 시리얼라이저
│   ├── urls.py                # 앱 URL 라우팅
│   ├── views.py               # API 뷰
│   └── tests.py               # 테스트 파일
├── api_data/                  # CSV 데이터 저장소
│   └── .gitkeep               # 폴더 유지용 파일
├── Dockerfile                 # Docker 이미지 설정
├── requirements.txt           # Python 의존성
├── load_initial_data.py       # 초기 데이터 로드 스크립트
├── manage.py                  # Django 관리 스크립트
└── README.md                  # 이 파일
```

## 🗄️ 데이터베이스 모델

### 1. 여행지 관련 모델

#### `Destination`
- **기능**: 서울 여행지 정보 저장
- **필드**:
  - `name`: 장소명
  - `area`: 지역 (강남구, 종로구 등)
  - `rating`: 평점 (0.0-5.0)
  - `duration`: 소요시간
  - `short_description`: 간단 설명
  - `long_description`: 상세 설명
  - `image_url`: 이미지 URL

#### `DestinationTag`
- **기능**: 여행지 태그 관리
- **필드**:
  - `destination`: 여행지 외래키
  - `tag_name`: 태그명 (산책, 전통, 쇼핑 등)

### 2. 사용자 관련 모델

#### `User`
- **기능**: 사용자 정보 관리
- **필드**:
  - `name`: 사용자명
  - `email`: 이메일 (고유)
  - `password`: 비밀번호

#### `Wishlist`
- **기능**: 사용자 찜 목록
- **필드**:
  - `user`: 사용자 외래키
  - `destination`: 여행지 외래키

#### `Trip`
- **기능**: 여행 계획 저장
- **필드**:
  - `user`: 사용자 외래키
  - `title`: 여행 제목
  - `duration`: 여행 기간
  - `style`: 여행 스타일
  - `budget`: 예산
  - `companions`: 동행자

### 3. 날씨 관련 모델 (새로운 구조)

#### `CurrentWeather`
- **기능**: 현재 날씨 정보 (서울 25개 구)
- **필드**:
  - `region`: 지역명 (강남구, 종로구 등)
  - `date`: 날짜 (YYYYMMDD)
  - `time`: 시간 (HHMM)
  - `temperature`: 기온 (°C)
  - `humidity`: 습도 (%)
  - `wind_speed`: 풍속 (m/s)
  - `rainfall`: 강수량 (mm)

#### `ShortForecast`
- **기능**: 단기 예보 (3일간)
- **필드**:
  - `region`: 지역명
  - `date`: 예보 날짜
  - `forecast_time`: 예보 시간
  - `temperature`: 기온
  - `wind_speed`: 풍속
  - `precipitation`: 강수량

#### `MidForecast`
- **기능**: 중기 예보 (10일간) - 여행 추천용
- **필드**:
  - `region`: 지역명 (서울)
  - `date`: 예보 날짜
  - `period`: 시간대 (Am, Pm, 하루)
  - `weather_condition`: 날씨 상태
  - `rain_probability`: 강수확률 (%)
  - `min_temperature`: 최저기온
  - `max_temperature`: 최고기온

## 🔌 API 엔드포인트

### 1. 여행지 API
```
GET /api/destinations/          # 여행지 목록
GET /api/destinations/{id}/     # 여행지 상세
```

### 2. 사용자 API
```
POST /api/users/login/          # 로그인
GET /api/users/                 # 사용자 목록
POST /api/users/                # 사용자 생성
```

### 3. 날씨 API (핵심 기능)
```
GET /api/weather/current/       # 현재 날씨 (서울 25개 구)
GET /api/weather/mid-forecast/  # 중기 예보 (여행 추천용)
GET /api/weather/statistics/    # 날씨 데이터 통계
```

## 🌤️ 날씨 서비스 상세

### `weather_api.py`
- **기능**: 기상청 API 연동
- **주요 함수**:
  - `get_current_weather(nx, ny)`: 현재 날씨 조회
  - `get_short_forecast(nx, ny)`: 단기 예보 조회
  - `get_mid_forecast(region_id)`: 중기 예보 조회
- **API 연동**:
  - 기상청 단기예보 API
  - 기상청 중기예보 API (육상, 기온)

### `weather_service.py`
- **기능**: 날씨 데이터 처리 및 관리
- **주요 메서드**:
  - `collect_save_and_load()`: 전체 파이프라인 실행
  - `get_current_weather_summary()`: 현재 날씨 요약
  - `collect_and_save_to_csv()`: CSV 저장
  - `load_csv_to_db()`: CSV → DB 로드
  - `cleanup_old_csv_files()`: 오래된 CSV 정리

### 날씨 데이터 파이프라인
```
1. API 수집 → 2. CSV 저장 → 3. DB 로드 → 4. CSV 정리
```

## 🔧 주요 서비스 파일

### `settings.py`
- **기능**: Django 프로젝트 설정
- **주요 설정**:
  - 데이터베이스 연결 (MySQL)
  - CORS 설정 (프론트엔드 연동)
  - REST Framework 설정
  - 기상청 API 키 설정

### `views.py`
- **기능**: API 뷰 정의
- **주요 뷰**:
  - `DestinationViewSet`: 여행지 CRUD
  - `current_weather()`: 현재 날씨 API
  - `get_weather_statistics()`: 날씨 통계 API
  - `collect_weather_data()`: 날씨 수집 API (관리자용)

### `serializers.py`
- **기능**: API 데이터 직렬화
- **주요 시리얼라이저**:
  - `DestinationSerializer`: 여행지 데이터
  - `CurrentWeatherSerializer`: 현재 날씨
  - `MidForecastSerializer`: 중기 예보

### `admin.py`
- **기능**: Django 관리자 페이지 설정
- **관리 모델**:
  - 여행지, 사용자, 찜 목록, 여행 계획
  - 날씨 데이터 (현재, 단기, 중기)

## 🐳 Docker 설정

### `Dockerfile`
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
```

### `docker-compose.yml` (루트)
```yaml
services:
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql]
```

## 📦 의존성 (requirements.txt)

### 주요 라이브러리
```
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
PyMySQL==1.1.0
pandas==2.1.3
requests==2.31.0
python-dotenv==1.0.0
```

## 🔧 관리 명령어

### `collect_weather.py`
- **기능**: 날씨 데이터 수집 Django 명령어
- **사용법**: `python manage.py collect_weather`
- **동작**: 전체 파이프라인 실행

### 기본 Django 명령어
```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser

# 개발 서버 실행
python manage.py runserver
```

## 🗃️ 데이터 관리

### 초기 데이터 로드
```bash
# 여행지 데이터 로드
python manage.py loaddata destinations/fixtures/destinations.json

# 또는 스크립트 실행
python load_initial_data.py
```

### 날씨 데이터 수집
```bash
# 최신 날씨 데이터 수집
python manage.py collect_weather
```

### CSV 파일 관리
- **저장 위치**: `api_data/` 폴더
- **자동 정리**: 1일 이상 된 파일 자동 삭제
- **수동 정리**: `cleanup_old_csv_files()` 메서드

## 🔍 API 응답 예시

### 현재 날씨 API
```json
{
  "success": true,
  "data": {
    "강남구": {
      "기온(℃)": "21.2",
      "습도(%)": "64",
      "풍속(m/s)": "1.7",
      "강수량(mm)": "0.0"
    }
  }
}
```

### 중기 예보 API
```json
{
  "success": true,
  "data": [
    {
      "region": "서울",
      "date": "20250925",
      "period": "Am",
      "weather_condition": "맑음",
      "rain_probability": 10,
      "min_temperature": 18.0,
      "max_temperature": 25.0
    }
  ]
}
```

## 🔐 보안 설정

### CORS 설정
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

### API 키 관리
- 환경변수로 기상청 API 키 관리
- `.env` 파일 사용 (git 제외)

## 📊 데이터 플로우

### 날씨 데이터 수집 플로우
```
기상청 API → CSV 저장 → 데이터 검증 → DB 저장 → 구버전 정리
```

### API 요청 플로우
```
프론트엔드 → Django View → Service Layer → Model → Database
```

## 🧪 테스트

### API 테스트
```bash
# 현재 날씨 API 테스트
curl http://localhost:8000/api/weather/current/

# 통계 API 테스트
curl http://localhost:8000/api/weather/statistics/
```

### 데이터 확인
```bash
# Django Shell에서 데이터 확인
python manage.py shell
>>> from destinations.models import CurrentWeather
>>> CurrentWeather.objects.count()
```

## 🔄 정기 업데이트

### 날씨 데이터 자동 업데이트
- 수동 실행: `python manage.py collect_weather`
- 스케줄링: cron job 또는 celery 사용 가능

### 데이터 백업
- MySQL 덤프 생성
- CSV 파일 백업 (선택사항)