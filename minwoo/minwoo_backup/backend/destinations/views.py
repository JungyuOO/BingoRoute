from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.http import JsonResponse
from .models import Destination, User, Wishlist, Trip, CurrentWeather, ShortForecast, MidForecast
import datetime
from .serializers import (
    DestinationSerializer, UserSerializer, 
    WishlistSerializer, TripSerializer
)
from .services.weather_service import WeatherService

class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

    def get_queryset(self):
        queryset = Destination.objects.all()
        
        # 검색 기능
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(area__icontains=search) |
                Q(short_description__icontains=search) |
                Q(tags__tag_name__icontains=search)
            ).distinct()
        
        # 태그 필터링
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__tag_name=tag)
        
        # 평점 필터링
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        
        return queryset

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email, password=password)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Wishlist.objects.filter(user_id=user_id)
        return Wishlist.objects.none()

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Trip.objects.filter(user_id=user_id)
        return Trip.objects.none()

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
    """날씨 데이터 수집 및 DB 저장 (관리자용)"""
    try:
        result = WeatherService.collect_save_and_load()
        return JsonResponse({
            'success': True,
            'message': f'전체 파이프라인 완료! 총 {result["total_records"]}건 저장',
            'data': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def export_weather_csv(request):
    """날씨 데이터 CSV 내보내기"""
    try:
        filename = WeatherService.export_to_csv()
        return JsonResponse({
            'success': True,
            'message': f'CSV 파일이 생성되었습니다: {filename}',
            'filename': filename
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def collect_csv_only(request):
    """날씨 데이터를 CSV로만 저장 (DB 저장 안함)"""
    try:
        result = WeatherService.collect_and_save_to_csv()
        return JsonResponse({
            'success': True,
            'message': 'CSV 파일 생성 완료',
            'data': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def load_csv_to_db(request):
    """CSV 파일을 DB에 로드"""
    csv_file = request.data.get('csv_file')
    if not csv_file:
        return JsonResponse({
            'success': False,
            'error': 'csv_file 파라미터가 필요합니다.'
        }, status=400)
    
    try:
        count = WeatherService.load_csv_to_db(csv_file)
        return JsonResponse({
            'success': True,
            'message': f'{count}건의 데이터를 DB에 저장했습니다.',
            'count': count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_mid_forecast_for_algorithm(request):
    """추천 알고리즘용 중기예보 데이터 조회"""
    try:
        # 향후 7일간의 중기예보 데이터
        today = datetime.date.today()
        end_date = (today + datetime.timedelta(days=7)).strftime("%Y%m%d")
        
        mid_forecasts = MidForecast.objects.filter(
            date__gte=today.strftime("%Y%m%d"),
            date__lte=end_date
        ).values(
            'region', 'date', 'period', 'weather_condition', 
            'rain_probability', 'min_temperature', 'max_temperature'
        )
        
        return JsonResponse({
            'success': True,
            'data': list(mid_forecasts)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_weather_statistics(request):
    """날씨 데이터 통계 조회"""
    try:
        current_count = CurrentWeather.objects.count()
        short_count = ShortForecast.objects.count()
        mid_count = MidForecast.objects.count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_weather': current_count,
                'short_forecast': short_count,
                'mid_forecast': mid_count,
                'legacy_data': 0,  # WeatherData 테이블 제거됨
                'total': current_count + short_count + mid_count
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)