from rest_framework import serializers
from .models import (
    Destination, DestinationTag, User, Wishlist, Trip, 
    CurrentWeather, ShortForecast, MidForecast
)

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
        fields = ['id', 'name', 'email', 'created_at']
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
class CurrentWeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentWeather
        fields = [
            'id', 'region', 'date', 'time', 'temperature', 
            'humidity', 'wind_speed', 'rainfall', 'created_at'
        ]

class ShortForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortForecast
        fields = [
            'id', 'region', 'date', 'forecast_time', 'temperature',
            'wind_speed', 'precipitation', 'created_at'
        ]

class MidForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = MidForecast
        fields = [
            'id', 'region', 'date', 'period', 'weather_condition',
            'rain_probability', 'min_temperature', 'max_temperature', 'created_at'
        ]

# WeatherDataSerializer 제거됨 - 새로운 테이블 구조 사용