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
        fields = '__all__'


# 여행별 관광지 목록 직렬화기
class UserTourItinerarySerializer(serializers.ModelSerializer):

    class Meta:
        model = MemberTripItinerary
        fields = '__all__'
