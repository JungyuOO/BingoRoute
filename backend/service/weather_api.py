from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiExample

from .weather_service import WeatherService


@extend_schema(
    tags=['날씨'],
    summary='서울 구별 단기 예보 요약',
    description=(
        '서울 25개 구에 대한 가장 가까운 단기 예보 시각의 기온·풍속·강수량을 반환합니다. '
        '실시간 API 호출이 실패하면 CSV 스냅샷 데이터를 사용합니다.'
    ),
    responses={
        200: OpenApiExample(
            '성공 예시',
            value={
                "success": True,
                "data": {
                    "timestamp": "2025-11-03T11:40:00+09:00",
                    "forecast_date": "20251103",
                    "forecast_time": "1200",
                    "display_date": "오늘",
                    "display_time": "12:00",
                    "regions": {
                        "강남구": {
                            "temp": "14",
                            "wind": "0.4 m/s",
                            "rainfall": "0",
                            "sky": "정보없음",
                            "advice": "여행하기 좋은 날씨입니다 ☀️",
                            "timeInfo": None,
                        }
                    },
                },
            },
            response_only=True,
        ),
    },
)
@api_view(['GET'])
def current_weather(request):
    """서울 각 구의 단기 예보 요약을 반환한다."""
    try:
        summary = WeatherService.get_short_forecast_summary()
        return JsonResponse({"success": True, "data": summary})
    except Exception as exc:  # pragma: no cover - 오류 응답
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
