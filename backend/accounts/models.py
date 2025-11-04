from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """Ensure PK is set to user_id when creating users."""

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if not user.id:
            user.id = user.user_id or username
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    # 기본 필드들 (AbstractUser에서 상속)
    # username, email, first_name, last_name, password 등

    id = models.CharField(max_length=50, primary_key=True, editable=False)

    # 추가 필드들
    user_id = models.CharField(max_length=50, unique=True, help_text="로그인용 ID")
    email = models.EmailField(unique=True, help_text="이메일 주소")
    birth_date = models.DateField(null=True, blank=True, help_text="생년월일")

    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        help_text="성별"
    )

    # 이메일 인증 관련
    is_email_verified = models.BooleanField(default=False, help_text="이메일 인증 여부")
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        help_text="이메일 인증 토큰"
    )

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    # 로그인 시 사용할 필드 설정
    USERNAME_FIELD = 'user_id'  # user_id로 로그인
    REQUIRED_FIELDS = ['email', 'first_name']  # 필수 필드

    class Meta:
        db_table = 'accounts_user'
        managed = False
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.user_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} ({self.first_name})"

    @property
    def display_name(self):
        """표시용 이름 반환"""
        return self.first_name or self.user_id
