import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache


def generate_verification_code():
    """6자리 인증 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email, code):
    """이메일 인증 코드 발송"""
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
    """인증 코드를 캐시에 저장 (5분 유효)"""
    cache_key = f"email_verification_{email}"
    cache.set(cache_key, code, timeout=300)  # 5분


def verify_email_code(email, code):
    """이메일 인증 코드 확인"""
    cache_key = f"email_verification_{email}"
    stored_code = cache.get(cache_key)
    
    if stored_code and stored_code == code:
        cache.delete(cache_key)  # 인증 성공 시 코드 삭제
        return True
    return False