import random
import string
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

# 시간 제한(초)
EMAIL_VERIFICATION_TIMEOUT = 300  # 5분
PASSWORD_RESET_TIMEOUT = 600      # 10분


def generate_verification_code():
    """6자리 인증 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email, code):
    """회원가입용 이메일 인증 코드 발송"""
    subject = '[BingoRoute] 이메일 인증 코드'
    message = f'''
안녕하세요!

BingoRoute 회원가입을 위한 이메일 인증 코드입니다.

인증 코드: {code}

이 코드를 회원가입 페이지에 입력해주세요.
코드는 5분간 유효합니다.

감사합니다.
BingoRoute 팀
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False


def store_verification_code(email, code):
    """이메일 인증 코드를 캐시에 저장"""
    cache_key = f"email_verification_{email.lower()}"
    cache.set(cache_key, code, timeout=EMAIL_VERIFICATION_TIMEOUT)


def verify_email_code(email, code):
    """이메일 인증 코드 확인"""
    cache_key = f"email_verification_{email.lower()}"
    stored_code = cache.get(cache_key)

    if stored_code and stored_code == code:
        cache.delete(cache_key)
        return True
    return False


def _password_reset_cache_key(user_id, email):
    return f"password_reset_{user_id.lower()}_{email.lower()}"


def send_password_reset_email(email, code):
    """비밀번호 재설정용 인증 코드 발송"""
    subject = '[BingoRoute] 비밀번호 재설정 인증 코드'
    message = f'''
안녕하세요!

BingoRoute 비밀번호 재설정을 위한 인증 코드입니다.

인증 코드: {code}

이 코드를 비밀번호 재설정 화면에 입력하고 새 비밀번호를 설정해주세요.
코드는 10분간 유효합니다.

감사합니다.
BingoRoute 팀
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"비밀번호 재설정 이메일 발송 실패: {e}")
        return False


def store_password_reset_code(user_id, email, code):
    """비밀번호 재설정 인증 코드를 캐시에 저장"""
    cache_key = _password_reset_cache_key(user_id, email)
    cache.set(cache_key, code, timeout=PASSWORD_RESET_TIMEOUT)


def verify_password_reset_code(user_id, email, code, *, consume=True):
    """비밀번호 재설정 인증 코드 확인

    consume=False로 호출하면 코드를 삭제하지 않고 존재 여부만 확인합니다.
    """
    cache_key = _password_reset_cache_key(user_id, email)
    stored_code = cache.get(cache_key)

    if stored_code and stored_code == code:
        if consume:
            cache.delete(cache_key)
        return True
    return False
