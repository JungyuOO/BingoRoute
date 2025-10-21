from django.contrib.auth import get_user_model, authenticate
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

User = get_user_model()  # CustomUser 모델 사용


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'User Response Example',
            summary='사용자 정보 응답 예시',
            description='로그인 성공 시 반환되는 사용자 정보',
            value={
                "id": 1,
                "user_id": "testuser123",
                "email": "test@example.com",
                "name": "홍길동",
                "display_name": "홍길동",
                "birth_date": "1990-01-01",
                "gender": "M",
                "is_email_verified": False
            }
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', read_only=True)
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "user_id", "email", "name", "display_name", "birth_date", "gender", "is_email_verified"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Signup Request Example',
            summary='회원가입 요청 예시',
            description='새로운 사용자 계정 생성을 위한 요청 데이터',
            value={
                "user_id": "testuser123",
                "name": "홍길동",
                "email": "test@example.com",
                "password": "password123!",
                "confirm_password": "password123!",
                "birth_date": "1990-01-01",
                "gender": "M"
            }
        )
    ]
)
class SignupSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=50, help_text="로그인에 사용할 사용자 ID")
    name = serializers.CharField(max_length=150, help_text="사용자 이름")
    email = serializers.EmailField(help_text="이메일 주소")
    password = serializers.CharField(write_only=True, min_length=8, help_text="비밀번호 (최소 8자)")
    confirm_password = serializers.CharField(write_only=True, min_length=8, help_text="비밀번호 확인")
    birth_date = serializers.DateField(required=False, help_text="생년월일 (선택사항)")
    gender = serializers.ChoiceField(
        choices=[('M', '남성'), ('F', '여성'), ('O', '기타')], 
        required=False,
        help_text="성별 (선택사항)"
    )

    def validate_user_id(self, value):
        user_id = (value or '').strip()
        if not user_id:
            raise serializers.ValidationError("사용자 ID를 입력해주세요.")
        if User.objects.filter(user_id=user_id).exists():
            raise serializers.ValidationError("이미 존재하는 사용자 ID입니다.")
        return user_id

    def validate_name(self, value):
        name = (value or '').strip()
        if not name:
            raise serializers.ValidationError("이름을 입력해주세요.")
        return name

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        user_id = validated_data["user_id"].strip()
        name = validated_data["name"].strip()
        email = validated_data["email"].lower()
        password = validated_data["password"]
        birth_date = validated_data.get("birth_date")
        gender = validated_data.get("gender")

        try:
            user = User.objects.create_user(
                username=user_id,  # AbstractUser의 username 필드
                user_id=user_id,   # 커스텀 필드
                email=email,
                password=password,
                first_name=name,
                birth_date=birth_date,
                gender=gender,
            )
        except IntegrityError:
            raise serializers.ValidationError({
                "user_id": "이미 존재하는 사용자 ID입니다.",
                "email": "이미 존재하는 이메일입니다.",
            })
        return user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Login Request Example',
            summary='로그인 요청 예시',
            description='사용자 로그인을 위한 요청 데이터',
            value={
                "user_id": "testuser123",
                "password": "password123!"
            }
        )
    ]
)
class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(help_text="사용자 ID")
    password = serializers.CharField(write_only=True, help_text="비밀번호")

    def validate(self, attrs):
        user_id = attrs.get("user_id", "").strip()
        password = attrs.get("password", "")
        
        # user_id로 사용자 찾기
        try:
            user_obj = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("사용자 ID 또는 비밀번호가 올바르지 않습니다.")

        # 인증 (username 필드 사용)
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError("사용자 ID 또는 비밀번호가 올바르지 않습니다.")

        attrs["user"] = user
        attrs["access"] = str(AccessToken.for_user(user))
        return attrs
