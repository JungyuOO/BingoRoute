from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .serializers import SignupSerializer, UserSerializer, LoginSerializer
from .utils import generate_verification_code, send_verification_email, store_verification_code, verify_email_code

User = get_user_model()


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
