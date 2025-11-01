# JSON 직렬화

from rest_framework import serializers
from .models import TouristSpot, TouristDetail, MemberTrip, MemberTripItinerary

# 관광지 직렬화기
class TouristSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristSpot
        fields = '__all__'

# 관광지 상세 직렬화기
class TouristDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristDetail
        fields = '__all__'

# 사용자별 여행 계획 직렬화기
class UserTourPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = ['trip_id', 'user_id', 'status', 'trip_title', 'travel_date', 'created_at', 'updated_at']


# 여행별 관광지 목록 직렬화기
class UserTourItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTripItinerary
        fields = ['trip_id', 'seq', 'content_id', 'visit_date', 'stay_time']
