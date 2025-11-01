# JSON 직렬화

from rest_framework import serializers
from .models import TouristSpot, TouristDetail, MemberTrip, MemberTripItinerary, Jjim

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


class JjimSerializer(serializers.ModelSerializer):
    content_id = serializers.CharField(read_only=True)

    class Meta:
        model = Jjim
        fields = ('content_id',)


class JjimCreateSerializer(serializers.ModelSerializer):
    content_id = serializers.SlugRelatedField(
        source='content',
        slug_field='content_id',
        queryset=TouristSpot.objects.all(),
    )

    class Meta:
        model = Jjim
        fields = ('user_id', 'content_id')

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        content = attrs.get('content')
        if user_id and content and Jjim.objects.filter(user_id=user_id, content=content).exists():
            raise serializers.ValidationError("이미 찜한 관광지입니다.")
        return attrs


class JjimDeleteSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    content_id = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        content_id = attrs.get('content_id')
        if not Jjim.objects.filter(user_id=user_id, content_id=content_id).exists():
            raise serializers.ValidationError("삭제할 찜 정보가 존재하지 않습니다.")
        return attrs
