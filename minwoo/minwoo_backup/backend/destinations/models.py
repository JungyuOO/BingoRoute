from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100, verbose_name='장소명')
    area = models.CharField(max_length=100, verbose_name='지역')
    rating = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='평점')
    duration = models.CharField(max_length=50, verbose_name='소요시간')
    short_description = models.TextField(verbose_name='간단 설명')
    long_description = models.TextField(verbose_name='상세 설명')
    image_url = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '여행지'
        verbose_name_plural = '여행지들'
        ordering = ['-rating', 'name']

    def __str__(self):
        return f"{self.name} ({self.area})"

class DestinationTag(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tags')
    tag_name = models.CharField(max_length=50, verbose_name='태그명')

    class Meta:
        verbose_name = '여행지 태그'
        verbose_name_plural = '여행지 태그들'
        unique_together = ['destination', 'tag_name']

    def __str__(self):
        return f"{self.destination.name} - {self.tag_name}"

class User(models.Model):
    name = models.CharField(max_length=100, verbose_name='이름')
    email = models.EmailField(unique=True, verbose_name='이메일')
    password = models.CharField(max_length=128, verbose_name='비밀번호')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return f"{self.name} ({self.email})"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '찜 목록'
        verbose_name_plural = '찜 목록들'
        unique_together = ['user', 'destination']

    def __str__(self):
        return f"{self.user.name} - {self.destination.name}"

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    title = models.CharField(max_length=200, verbose_name='여행 제목')
    duration = models.CharField(max_length=50, verbose_name='여행 기간')
    style = models.CharField(max_length=50, verbose_name='여행 스타일')
    budget = models.CharField(max_length=50, verbose_name='예산')
    companions = models.CharField(max_length=50, verbose_name='동행자')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '여행 계획'
        verbose_name_plural = '여행 계획들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.title}"

# 기본 날씨 데이터 (공통 필드)
class WeatherBase(models.Model):
    region = models.CharField(max_length=50, verbose_name='지역')
    date = models.CharField(max_length=8, verbose_name='날짜')  # YYYYMMDD
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 현재 날씨 (관측 데이터)
class CurrentWeather(WeatherBase):
    time = models.CharField(max_length=4, verbose_name='관측시간')  # HHMM
    temperature = models.FloatField(null=True, blank=True, verbose_name='기온(℃)')
    humidity = models.IntegerField(null=True, blank=True, verbose_name='습도(%)')
    wind_speed = models.FloatField(null=True, blank=True, verbose_name='풍속(m/s)')
    rainfall = models.FloatField(null=True, blank=True, verbose_name='강수량(mm)')
    
    class Meta:
        verbose_name = '현재 날씨'
        verbose_name_plural = '현재 날씨들'
        unique_together = ['region', 'date', 'time']
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.region} - {self.date} {self.time} - {self.temperature}°C"

# 단기 예보 (3일)
class ShortForecast(WeatherBase):
    forecast_time = models.CharField(max_length=4, verbose_name='예보시간')  # HHMM
    temperature = models.FloatField(null=True, blank=True, verbose_name='기온(℃)')
    wind_speed = models.FloatField(null=True, blank=True, verbose_name='풍속(m/s)')
    precipitation = models.CharField(max_length=20, null=True, blank=True, verbose_name='강수형태')
    
    class Meta:
        verbose_name = '단기 예보'
        verbose_name_plural = '단기 예보들'
        unique_together = ['region', 'date', 'forecast_time']
        ordering = ['-date', 'forecast_time']

    def __str__(self):
        return f"{self.region} - {self.date} {self.forecast_time} - {self.temperature}°C"

# 중기 예보 (10일)
class MidForecast(WeatherBase):
    period = models.CharField(max_length=10, verbose_name='예보구간')  # Am, Pm, 하루
    weather_condition = models.CharField(max_length=50, null=True, blank=True, verbose_name='날씨')
    rain_probability = models.IntegerField(null=True, blank=True, verbose_name='강수확률(%)')
    min_temperature = models.FloatField(null=True, blank=True, verbose_name='최저기온(℃)')
    max_temperature = models.FloatField(null=True, blank=True, verbose_name='최고기온(℃)')
    
    class Meta:
        verbose_name = '중기 예보'
        verbose_name_plural = '중기 예보들'
        unique_together = ['region', 'date', 'period']
        ordering = ['-date', 'period']

    def __str__(self):
        return f"{self.region} - {self.date} {self.period} - {self.weather_condition}"

# WeatherData 모델 제거됨 - 새로운 CurrentWeather, ShortForecast, MidForecast 사용