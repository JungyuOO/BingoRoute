from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Destination, DestinationTag, Wishlist, Trip,
    CodeTable, TouristSpot, TouristSpotDetail, MyVectors, 
    Jjim, MemberTrip, MemberTripItinerary
)

User = get_user_model()

class DestinationTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationTag
        fields = ['tag_name']

class DestinationSerializer(serializers.ModelSerializer):
    tags = DestinationTagSerializer(many=True, read_only=True)
    tag_names = serializers.SerializerMethodField()

    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'area', 'rating', 'duration', 
            'short_description', 'long_description', 'image_url',
            'tags', 'tag_names', 'created_at', 'updated_at'
        ]

    def get_tag_names(self, obj):
        return [tag.tag_name for tag in obj.tags.all()]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'first_name', 'email', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

class WishlistSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'destination', 'created_at']

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'duration', 'style', 'budget', 
            'companions', 'created_at'
        ]

# 날씨 데이터는 CSV 파일로 관리되므로 Serializer가 필요하지 않습니다

# 새로운 관광지 데이터베이스용 Serializers
class CodeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = ['code', 'name', 'upper_code', 'created_at', 'updated_at']

class TouristSpotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category_code.name', read_only=True)
    
    class Meta:
        model = TouristSpot
        fields = [
            'content_id', 'title', 'firstimage', 'firstimage2',
            'category_code', 'category_name', 'created_at', 'updated_at'
        ]

class TouristSpotDetailSerializer(serializers.ModelSerializer):
    tourist_spot_title = serializers.CharField(source='content_id.title', read_only=True)
    sigungu_code_name = serializers.CharField(source='address_code.name', read_only=True)
    
    class Meta:
        model = TouristSpotDetail
        fields = [
            'id', 'content_id', 'tourist_spot_title', 'address_code', 'sigungu_code_name',
            'sigungu_name', 'zip_code', 'address', 'map_x', 'map_y',
            'intro_serial_num', 'content_type_id', 'tel', 'restdate',
            'useseason', 'usetime', 'is_parking', 'is_baby_carriage',
            'is_pet', 'is_credit_card', 'info_serial_num', 'info_name',
            'info_text', 'created_at', 'updated_at'
        ]

class MyVectorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyVectors
        fields = ['id', 'content', 'metadata', 'created_at']
        # embedding 필드는 보통 API에서 직접 노출하지 않음

class JjimSerializer(serializers.ModelSerializer):
    tourist_spot_title = serializers.CharField(source='content_id.title', read_only=True)
    tourist_spot_image = serializers.CharField(source='content_id.firstimage', read_only=True)
    
    class Meta:
        model = Jjim
        fields = ['jjim_id', 'content_id', 'tourist_spot_title', 'tourist_spot_image', 'jjim_on_off']

class MemberTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = [
            'trip_id', 'status', 'trip_title', 'travel_date',
            'created_at', 'updated_at'
        ]

class MemberTripItinerarySerializer(serializers.ModelSerializer):
    tourist_spot_title = serializers.CharField(source='content_id.title', read_only=True)
    tourist_spot_image = serializers.CharField(source='content_id.firstimage', read_only=True)
    
    class Meta:
        model = MemberTripItinerary
        fields = [
            'trip_id', 'seq', 'content_id', 'tourist_spot_title', 
            'tourist_spot_image', 'visit_date', 'stay_time'
        ]

# 통합된 관광지 정보 Serializer (기본 정보 + 상세 정보)
class TouristSpotWithDetailSerializer(serializers.ModelSerializer):
    details = TouristSpotDetailSerializer(source='touristspotdetail_set', many=True, read_only=True)
    category_name = serializers.CharField(source='category_code.name', read_only=True)
    
    class Meta:
        model = TouristSpot
        fields = [
            'content_id', 'title', 'firstimage', 'firstimage2',
            'category_code', 'category_name', 'details', 'created_at', 'updated_at'
        ]