# JSON 직렬화

from rest_framework import serializers
from .models import TouristSpot, TouristDetail

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