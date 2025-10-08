from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import SignupSerializer, UserSerializer, LoginSerializer


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
