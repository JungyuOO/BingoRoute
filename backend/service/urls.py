from django.urls import path
from .tourist import TouristSpotAllView, TouristSpotDetailView, UserJjimView

urlpatterns = [
    path('tourist_spots/', TouristSpotAllView.as_view(), name='tourist-spot-all'),
    path('tourist_spots/detail/<str:content_id>/', TouristSpotDetailView.as_view(), name='tourist-spot-detail'),
    
    # 찜하기 관련 URL
    path('jjim/', UserJjimView.as_view(), name='user-jjim'),
    path('user/tour_plans/', UserTourPlanView.as_view(), name='user-tour-plans'),
    path('user/tour_plans/<str:user_id>/trip/<int:trip_id>/', UserTourPlanManageView.as_view(), name='user-tour-plan-detail'),
    path('user/tour_itineraries/', UserTourItineraryView.as_view(), name='user-tour-itineraries'),
    path('user/tour_itineraries/trip/<int:trip_id>/seq/<int:seq>/', UserTourItineraryManageView.as_view(), name='user-tour-itinerary-detail'),
    
    path('user/jjim/', UserJjimView.as_view(), name='user-jjim'),
  
    path('weather/current/', current_weather, name='weather-current'),
    path('weather/forecast/', weather_forecast, name='weather-forecast'),
    path('weather/collect/', collect_weather_data, name='weather-collect'),
    path('weather/mid-forecast/', get_mid_forecast_for_algorithm, name='weather-mid-forecast'),
    path('weather/statistics/', get_weather_statistics, name='weather-statistics'),
    path('weather/by-time/', get_weather_by_time, name='weather-by-time'),
]
