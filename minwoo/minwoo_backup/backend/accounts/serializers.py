from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken


class UserSerializer(serializers.ModelSerializer):
    # 표시용 이름은 first_name을 사용 (중복 허용)
    name = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name"]


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate_name(self, value):
        name = (value or '').strip()
        if not name:
            raise serializers.ValidationError("이름을 입력해주세요.")
        # 표시용 이름은 중복을 허용합니다.
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
        name = validated_data.get("name", "").strip()
        email = validated_data["email"].lower()
        password = validated_data["password"]

        try:
            # username은 고유해야 하므로 이메일을 사용하고, 표시용 이름은 first_name에 저장합니다.
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
            )
        except IntegrityError:
            # 이메일 중복 등 고유 제약 위반 시
            raise serializers.ValidationError({
                "email": "이미 존재하는 이메일입니다.",
            })
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        password = attrs.get("password", "")
        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

        # 기본 인증은 username 필드를 사용하므로, 조회한 사용자의 username으로 인증
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

        attrs["user"] = user
        attrs["access"] = str(AccessToken.for_user(user))
        return attrs
