# BINGOROUTE 인증 구현 가이드 (JWT)

- 작성일: 자동 생성
- 범위: 회원 DB 생성 → 회원가입(삽입) → 로그인(JWT 발급) → 인증 사용

## 개요
- 인증 방식: JWT Access 토큰(Stateless)
- 사용자 테이블: Django 기본 `auth_user`
- 이름 저장: `username` 컬럼에 저장, 이메일은 `email` 컬럼 사용

## 데이터베이스
- 테이블 생성: `python manage.py migrate` 실행 시 `auth_user` 포함 기본 테이블 생성
- 연결 설정: `backend/bingoroute_api/settings.py`:89
- 주요 컬럼
  - `username`: 이름 저장
  - `email`: 이메일 저장
  - `password`: 해시값 저장(Django `create_user` 사용)

## 설정(REST/JWT)
- DRF 설정: `backend/bingoroute_api/settings.py`:145
  - `DEFAULT_AUTHENTICATION_CLASSES = ['rest_framework_simplejwt.authentication.JWTAuthentication']`
- 패키지: `backend/requirements.txt`:1 에 `djangorestframework-simplejwt` 추가됨
- CORS: 헤더 기반 인증이므로 `CORS_ALLOW_CREDENTIALS = False`

## 시리얼라이저
- 파일: `backend/accounts/serializers.py`:1

### UserSerializer
- 목적: 사용자 응답용 직렬화
- 구현: `name`을 `username`에서 매핑
- 필드: `id`, `email`, `name`

### SignupSerializer
- 입력: `name`, `email`, `password`, `confirm_password`
- 검증
  - 이메일 중복: `validate_email`
  - 비밀번호/확인 일치: `validate`
- 생성(`create`)
  - `User.objects.create_user(username=name, email=email, password=password)`
  - 결과: `auth_user`에 레코드 INSERT, `password`는 해시 저장

### LoginSerializer
- 입력: `email`, `password`
- 처리
  - `User.objects.get(email__iexact=email)`로 사용자 조회
  - 조회된 사용자의 `username`으로 `authenticate(username=user.username, password=...)`
  - 성공 시 `AccessToken.for_user(user)`로 Access 토큰 발급
- 출력: `user`, `access`

## 뷰/URL
- URL 연결: `backend/bingoroute_api/urls.py`:22 → `path('api/auth/', include('accounts.urls'))`
- 엔드포인트 정의: `backend/accounts/urls.py`:5
  - `POST /api/auth/signup/` → 회원가입
  - `POST /api/auth/login/` → 로그인(JWT 발급)

### signup 뷰
- 파일: `backend/accounts/views.py`:9
- 동작: `SignupSerializer`로 검증/생성 후 `{ user }` 반환
- 요청 예시
```json
{
  "name": "홍길동",
  "email": "test@test.com",
  "password": "abcd1234",
  "confirm_password": "abcd1234"
}
```
- 응답 예시
```json
{ "user": { "id": 2, "email": "test@test.com", "name": "홍길동" } }
```

### login 뷰
- 파일: `backend/accounts/views.py`:25
- 동작: `LoginSerializer`로 자격 검증 후 `{ access, user }` 반환
- 요청 예시
```json
{ "email": "test@test.com", "password": "abcd1234" }
```
- 응답 예시
```json
{
  "access": "<JWT_ACCESS_TOKEN>",
  "user": { "id": 2, "email": "test@test.com", "name": "홍길동" }
}
```

## JWT 사용
- 보호된 API 호출 시 헤더 추가
```
Authorization: Bearer <access_token>
```
- DRF View에서 인증 강제 예시
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

@api_view(["GET"]) 
@permission_classes([IsAuthenticated])
def me(request):
    ...
```

## 프론트엔드 연동 요약
- 로그인 성공 후 응답 `{ access, user }`에서 `access`를 보관
- API 호출 시 `Authorization` 헤더에 Bearer 토큰 첨부

## 참고 파일 라인
- 설정: backend/bingoroute_api/settings.py:145
- URL 진입점: backend/bingoroute_api/urls.py:22
- Auth URLs: backend/accounts/urls.py:5
- 시리얼라이저: backend/accounts/serializers.py:7,16,46
- 뷰: backend/accounts/views.py:9,25

---
