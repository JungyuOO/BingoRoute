from rest_framework.decorators import api_view
from django.http import JsonResponse
from .weather_service import WeatherService


@api_view(['GET'])
def current_weather(request):
    """현재 날씨 정보 조회"""
    try:
        weather_data = WeatherService.get_current_weather_summary()
        return JsonResponse({
            'success': True,
            'data': weather_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def weather_forecast(request):
    """날씨 예보 조회"""
    region = request.GET.get('region', None)
    days = int(request.GET.get('days', 3))

    try:
        forecast_data = WeatherService.get_weather_forecast(region, days)
        return JsonResponse({
            'success': True,
            'data': list(forecast_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def collect_weather_data(request):
    """날씨 데이터 수집 및 CSV 저장 (관리자용)"""
    try:
        result = WeatherService.collect_and_save_to_csv()
        return JsonResponse({
            'success': True,
            'message': f'날씨 데이터 CSV 저장 완료! 단기:{result["short_count"]}건, 중기:{result["mid_count"]}건',
            'data': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_mid_forecast_for_algorithm(request):
    """추천 알고리즘용 중기예보 데이터 조회 (CSV 기반)"""
    try:
        forecast_data = WeatherService.get_mid_forecast_for_algorithm()
        return JsonResponse({
            'success': True,
            'data': forecast_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_weather_statistics(request):
    """날씨 데이터 통계 조회 (CSV 기반)"""
    try:
        stats = WeatherService.get_weather_statistics()
        return JsonResponse({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_weather_by_time(request):
    """특정 시간대의 서울 구별 날씨 조회"""
    target_date = request.GET.get('date', None)  # YYYYMMDD 형식
    target_time = request.GET.get('time', None)  # HHMM 형식

    try:
        weather_data = WeatherService.get_weather_by_time(target_date, target_time)
        return JsonResponse({
            'success': True,
            'data': weather_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
