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

def _generate_title(user_id: str) -> str:
    count = MemberTrip.objects.filter(user_id=user_id).count() + 1
    return f"untitled-{count}"


class UserTourPlanReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = ['trip_id', 'user_id', 'status', 'trip_title', 'travel_date', 'created_at', 'updated_at']


class UserTourPlanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = ['status', 'trip_title', 'travel_date']

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        if not user_id:
            raise serializers.ValidationError({"user_id": "user_id is required"})
        title = validated_data.get('trip_title')
        if not title:
            validated_data['trip_title'] = _generate_title(user_id)
        return MemberTrip.objects.create(user_id=user_id, **validated_data)


class UserTourPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = ['status', 'trip_title', 'travel_date']

    def update(self, instance, validated_data):
        title = validated_data.get('trip_title')
        if title == '':
            validated_data['trip_title'] = _generate_title(instance.user_id)
        return super().update(instance, validated_data)


class UserTourItineraryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTripItinerary
        fields = ['trip_id', 'seq', 'content_id', 'visit_date', 'stay_time']


class UserTourItineraryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTripItinerary
        fields = ['seq', 'content_id', 'visit_date', 'stay_time']

    def create(self, validated_data):
        trip_id = self.context.get('trip_id')
        if trip_id is None:
            raise serializers.ValidationError({"trip_id": "trip_id is required"})
        return MemberTripItinerary.objects.create(trip_id_id=trip_id, **validated_data)


class UserTourItineraryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTripItinerary
        fields = ['seq', 'content_id', 'visit_date', 'stay_time']


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
