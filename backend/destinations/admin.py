from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Destination, DestinationTag, Wishlist, Trip

User = get_user_model()

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
    list_display = ['user_id', 'first_name', 'email', 'created_at']
    search_fields = ['user_id', 'first_name', 'email']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'created_at']
    list_filter = ['created_at']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'duration', 'style', 'created_at']
    list_filter = ['duration', 'style', 'created_at']
    search_fields = ['title', 'user__user_id', 'user__first_name']
    
# 날씨 데이터는 CSV 파일로 관리됩니다