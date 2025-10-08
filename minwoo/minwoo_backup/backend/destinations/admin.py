from django.contrib import admin
from .models import (
    Destination, DestinationTag, User, Wishlist, Trip, 
    CurrentWeather, ShortForecast, MidForecast
)

class DestinationTagInline(admin.TabularInline):
    model = DestinationTag
    extra = 1

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'rating', 'duration', 'created_at']
    list_filter = ['area', 'rating', 'created_at']
    search_fields = ['name', 'area', 'short_description']
    inlines = [DestinationTagInline]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'created_at']
    list_filter = ['created_at']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'duration', 'style', 'created_at']
    list_filter = ['duration', 'style', 'created_at']
    search_fields = ['title', 'user__name']
    
@admin.register(CurrentWeather)
class CurrentWeatherAdmin(admin.ModelAdmin):
    list_display = ['region', 'date', 'time', 'temperature', 'humidity', 'wind_speed', 'rainfall']
    list_filter = ['region', 'date']
    search_fields = ['region']
    ordering = ['-date', '-time']

@admin.register(ShortForecast)
class ShortForecastAdmin(admin.ModelAdmin):
    list_display = ['region', 'date', 'forecast_time', 'temperature', 'wind_speed', 'precipitation']
    list_filter = ['region', 'date']
    search_fields = ['region']
    ordering = ['-date', 'forecast_time']

@admin.register(MidForecast)
class MidForecastAdmin(admin.ModelAdmin):
    list_display = ['region', 'date', 'period', 'weather_condition', 'rain_probability', 'min_temperature', 'max_temperature']
    list_filter = ['region', 'date', 'period']
    search_fields = ['region', 'weather_condition']
    ordering = ['-date', 'period']

# WeatherDataAdmin 제거됨 - 새로운 테이블 구조 사용