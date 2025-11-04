from django.urls import path
from .tourist_api import TouristSpotAllView, TouristSpotDetailView
from .user_trips_api import (
    UserTourPlanView,
    UserTourItineraryView,
    UserTourPlanManageView,
    UserTourItineraryManageView,
)

from .user_jjim_api import UserJjimView
from .weather_api import current_weather

urlpatterns = [
    path('tourist_spots/', TouristSpotAllView.as_view(), name='tourist-spot-all'),
    path('tourist_spots/detail/<str:content_id>/', TouristSpotDetailView.as_view(), name='tourist-spot-detail'),
    
    path('user/tour_plans/', UserTourPlanView.as_view(), name='user-tour-plans'),
    path('user/tour_plans/<str:user_id>/trip/<int:trip_id>/', UserTourPlanManageView.as_view(), name='user-tour-plan-detail'),
    path('user/tour_itineraries/', UserTourItineraryView.as_view(), name='user-tour-itineraries'),
    path('user/tour_itineraries/trip/<int:trip_id>/seq/<int:seq>/', UserTourItineraryManageView.as_view(), name='user-tour-itinerary-detail'),
    
    path('user/jjim/', UserJjimView.as_view(), name='user-jjim'),
  
    path('weather/current/', current_weather, name='weather-current'),
]
