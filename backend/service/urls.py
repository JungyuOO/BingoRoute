from django.urls import path
from .tourist import TouristSpotAllView, TouristSpotDetailView, UserJjimView

urlpatterns = [
    path('tourist_spots/', TouristSpotAllView.as_view(), name='tourist-spot-all'),
    path('tourist_spots/detail/<str:content_id>/', TouristSpotDetailView.as_view(), name='tourist-spot-detail'),
    
    # 찜하기 관련 URL
    path('jjim/', UserJjimView.as_view(), name='user-jjim'),
]
