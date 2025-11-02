import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class ChatProxyView(APIView):
    # 인증 없이 호출 가능, CSRF 영향 방지를 위해 인증 비활성화
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    Proxy to local Ollama server.
    POST body: { messages: [{role, content}], model?: str, system?: str }
    Returns: { role: 'assistant', content: str, raw?: object }
    """

    def get(self, request):
        """헬스체크/모델 확인용."""
        return Response({
            'ok': True,
            'model': os.getenv('OLLAMA_MODEL', 'gemma3:1b'),
            'ollama_url': os.getenv('OLLAMA_URL', 'http://localhost:11434')
        })

    def post(self, request):
        messages = request.data.get('messages') or []
        # 기본 모델을 gemma3:1b로 설정 (env 또는 요청 본문으로 재정의 가능)
        model = request.data.get('model') or os.getenv('OLLAMA_MODEL', 'gemma3:1b')
        system_prompt = request.data.get('system') or (
            '당신은 서울 여행을 돕는 AI 플래너입니다. '
            '간결하고 친절하게 답하고, 일정 제안/교통/날씨 팁을 짧은 문장으로 제시하세요.'
        )

        # Ensure system message first
        normalized = []
        has_system = False
        for m in messages:
            role = m.get('role')
            content = m.get('content')
            if not role or content is None:
                continue
            if role == 'system':
                has_system = True
            normalized.append({'role': role, 'content': str(content)})
        if not has_system:
            normalized.insert(0, {'role': 'system', 'content': system_prompt})

        base_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        url = f"{base_url.rstrip('/')}/api/chat"
        payload = {
            'model': model,
            'messages': normalized,
            'stream': False,
        }

        try:
            # 간단한 서버 로그로 호출 여부 추적
            print('[ChatProxy] request ->', {'model': model, 'msg_len': len(normalized)})
            resp = requests.post(url, json=payload, timeout=60)
        except requests.exceptions.ConnectionError:
            return Response(
                {'error': 'Ollama 서버에 연결할 수 없습니다. Ollama가 로컬에서 실행 중인지 확인하세요.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except requests.exceptions.Timeout:
            return Response(
                {'error': 'Ollama 응답 시간이 초과되었습니다.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            return Response({'error': f'요청 실패: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not resp.ok:
            return Response(
                {'error': f'Ollama 오류: HTTP {resp.status_code}', 'detail': safe_json(resp)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = resp.json()
        message = (data or {}).get('message') or {}
        content = message.get('content') or ''
        result = {
            'role': 'assistant',
            'content': content,
            'raw': data,
        }
        # 빈 응답일 때도 왜 그런지 추적할 수 있도록 원본 포함
        if not content:
            result['note'] = 'empty_content_from_model'
        return Response(
            result,
            status=status.HTTP_200_OK,
        )


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        try:
            return resp.text
        except Exception:
            return None
