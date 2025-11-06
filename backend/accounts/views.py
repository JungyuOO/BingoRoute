from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    SignupSerializer,
    UserSerializer,
    LoginSerializer,
    FindIDSerializer,
    PasswordResetRequestSerializer,
    PasswordResetCodeVerifySerializer,
    PasswordResetConfirmSerializer,
)
from .utils import (
    generate_verification_code,
    send_verification_email,
    store_verification_code,
    verify_email_code,
    send_password_reset_email,
    store_password_reset_code,
    verify_password_reset_code,
)

User = get_user_model()


@extend_schema(
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다.",
    request=SignupSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiExample(
            'Bad Request',
            value={"user_id": ["이미 존재하는 사용자 ID입니다."]},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    # 선택: 회원가입 후 즉시 액세스 토큰 발급이 필요하면 아래 주석을 해제하세요.
    # from rest_framework_simplejwt.tokens import AccessToken
    # access = str(AccessToken.for_user(user))
    return Response({
        "user": UserSerializer(user).data,
        # "access": access,
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="로그인",
    description="사용자 ID와 비밀번호로 로그인하여 액세스 토큰을 발급받습니다.",
    request=LoginSerializer,
    responses={
        200: OpenApiExample(
            'Login Success',
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": "testuser123",
                    "user_id": "testuser123",
                    "email": "test@example.com",
                    "name": "홍길동",
                    "display_name": "홍길동"
                }
            },
            response_only=True
        ),
        400: OpenApiExample(
            'Login Failed',
            value={"detail": "사용자 ID 또는 비밀번호가 올바르지 않습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"detail": serializer.errors.get("non_field_errors", serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
    access = serializer.validated_data["access"]
    user = serializer.validated_data["user"]
    return Response({
        "access": access,
        "user": UserSerializer(user).data,
    })


@extend_schema(
    summary="세션 확인",
    description="전달된 액세스 토큰이 유효한지 확인하고 사용자 정보를 반환합니다.",
    responses={
        200: OpenApiExample(
            'Session Valid',
            value={
                "user": {
                    "id": "testuser123",
                    "user_id": "testuser123",
                    "email": "test@example.com",
                    "name": "홍길동",
                    "display_name": "홍길동"
                }
            },
            response_only=True
        ),
        401: OpenApiExample(
            'Unauthorized',
            value={"detail": "자격 증명이 제공되지 않았습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_view(request):
    return Response({
        "user": UserSerializer(request.user).data,
    })


@extend_schema(
    summary="이메일 인증 코드 발송",
    description="회원가입 시 이메일 인증을 위한 인증 코드를 발송합니다.",
    request={
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email', 'description': '인증 코드를 받을 이메일 주소'}
        },
        'required': ['email']
    },
    responses={
        200: OpenApiExample(
            'Success',
            value={"message": "인증 코드가 발송되었습니다."},
            response_only=True
        ),
        400: OpenApiExample(
            'Bad Request',
            value={"detail": "이미 가입된 이메일입니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_verification(request):
    """이메일 인증 코드 발송"""
    email = request.data.get('email')
    
    if not email:
        return Response({"detail": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 이미 가입된 이메일인지 확인
    if User.objects.filter(email__iexact=email).exists():
        return Response({"detail": "이미 가입된 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 인증 코드 생성 및 발송
    code = generate_verification_code()
    
    if send_verification_email(email, code):
        store_verification_code(email, code)
        return Response({"message": "인증 코드가 발송되었습니다."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "이메일 발송에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="이메일 인증 코드 확인",
    description="발송된 이메일 인증 코드를 확인합니다.",
    request={
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email', 'description': '인증할 이메일 주소'},
            'code': {'type': 'string', 'description': '이메일로 받은 6자리 인증 코드'}
        },
        'required': ['email', 'code']
    },
    responses={
        200: OpenApiExample(
            'Success',
            value={"message": "이메일 인증이 완료되었습니다."},
            response_only=True
        ),
        400: OpenApiExample(
            'Bad Request',
            value={"detail": "인증 코드가 올바르지 않거나 만료되었습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_code_view(request):
    """이메일 인증 코드 확인"""
    email = request.data.get('email')
    code = request.data.get('code')
    
    if not email or not code:
        return Response({"detail": "이메일과 인증 코드를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    if verify_email_code(email, code):
        return Response({"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "인증 코드가 올바르지 않거나 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="아이디 찾기",
    description="가입 시 등록한 이름과 이메일로 사용자 ID를 조회합니다.",
    request=FindIDSerializer,
    responses={
        200: OpenApiExample(
            'Find ID Success',
            value={"user_id": "testuser123"},
            response_only=True
        ),
        400: OpenApiExample(
            'Find ID Failed',
            value={"detail": "입력하신 정보와 일치하는 계정을 찾을 수 없습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def find_id_view(request):
    serializer = FindIDSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]
    return Response({"user_id": user.user_id}, status=status.HTTP_200_OK)


@extend_schema(
    summary="비밀번호 재설정 코드 발송",
    description="아이디, 이름, 이메일이 일치하는 사용자에게 비밀번호 재설정 인증 코드를 발송합니다.",
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiExample(
            'Password Reset Code Sent',
            value={"message": "비밀번호 재설정 인증 코드가 발송되었습니다."},
            response_only=True
        ),
        400: OpenApiExample(
            'Password Reset Code Failed',
            value={"detail": "입력하신 정보와 일치하는 계정을 찾을 수 없습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_send_code(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]
    code = generate_verification_code()

    if not send_password_reset_email(user.email, code):
        return Response({"detail": "이메일 발송에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    store_password_reset_code(user.user_id, user.email, code)
    return Response({"message": "비밀번호 재설정 인증 코드가 발송되었습니다."}, status=status.HTTP_200_OK)


@extend_schema(
    summary="비밀번호 재설정 코드 확인",
    description="발송된 인증 코드가 올바른지 확인합니다.",
    request=PasswordResetCodeVerifySerializer,
    responses={
        200: OpenApiExample(
            'Password Reset Code Verified',
            value={"message": "인증 코드가 확인되었습니다."},
            response_only=True
        ),
        400: OpenApiExample(
            'Password Reset Code Verify Failed',
            value={"detail": "인증 코드가 올바르지 않거나 만료되었습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_verify_code(request):
    serializer = PasswordResetCodeVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]
    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"]

    if not verify_password_reset_code(user.user_id, email, code, consume=False):
        return Response({"detail": "인증 코드가 올바르지 않거나 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "인증 코드가 확인되었습니다."}, status=status.HTTP_200_OK)


@extend_schema(
    summary="비밀번호 재설정",
    description="인증 코드를 검증하고 새 비밀번호를 설정합니다.",
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiExample(
            'Password Reset Success',
            value={"message": "비밀번호가 재설정되었습니다."},
            response_only=True
        ),
        400: OpenApiExample(
            'Password Reset Failed',
            value={"detail": "인증 코드가 올바르지 않거나 만료되었습니다."},
            response_only=True
        )
    },
    tags=["회원관리"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]
    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"]
    new_password = serializer.validated_data["new_password"]

    if not verify_password_reset_code(user.user_id, email, code, consume=True):
        return Response({"detail": "인증 코드가 올바르지 않거나 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save(update_fields=['password'])
    return Response({"message": "비밀번호가 재설정되었습니다."}, status=status.HTTP_200_OK)
