from django.db import models
from django.contrib.auth import get_user_model
from pgvector.django import VectorField
import numpy as np

User = get_user_model()

# 기존 모델들 (호환성 유지)
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

# 새로운 관광지 데이터베이스 모델들
class CodeTable(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    upper_code = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'code_table'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '코드 테이블'
        verbose_name_plural = '코드 테이블들'

    def __str__(self):
        return f"{self.code} - {self.name}"

class TouristSpot(models.Model):
    content_id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=200)
    firstimage = models.CharField(max_length=500, blank=True, null=True)
    firstimage2 = models.CharField(max_length=500, blank=True, null=True)
    category_code = models.ForeignKey(CodeTable, on_delete=models.SET_NULL, null=True, blank=True)
    category_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tourist_spot'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '관광지'
        verbose_name_plural = '관광지들'

    def __str__(self):
        return self.title

class TouristSpotDetail(models.Model):
    content_id = models.ForeignKey(TouristSpot, on_delete=models.CASCADE)
    address_code = models.ForeignKey(CodeTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='tourist_spots')
    sigungu_name = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    map_x = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    map_y = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    intro_serial_num = models.IntegerField(null=True, blank=True)
    content_type_id = models.CharField(max_length=10, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    restdate = models.TextField(blank=True, null=True)
    useseason = models.TextField(blank=True, null=True)
    usetime = models.TextField(blank=True, null=True)
    is_parking = models.SmallIntegerField(null=True, blank=True)
    is_baby_carriage = models.SmallIntegerField(null=True, blank=True)
    is_pet = models.SmallIntegerField(null=True, blank=True)
    is_credit_card = models.SmallIntegerField(null=True, blank=True)
    info_serial_num = models.CharField(max_length=50, blank=True, null=True)
    info_name = models.CharField(max_length=200, blank=True, null=True)
    info_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tourist_spot_detail'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '관광지 상세정보'
        verbose_name_plural = '관광지 상세정보들'
        unique_together = ['content_id', 'intro_serial_num', 'info_serial_num']

    def __str__(self):
        return f"{self.content_id.title} - 상세정보"

class MyVectors(models.Model):
    content = models.TextField()
    embedding = VectorField(dimensions=1536)  # OpenAI 임베딩 차원
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'my_vectors'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = 'RAG 벡터'
        verbose_name_plural = 'RAG 벡터들'

    def __str__(self):
        return f"Vector {self.id} - {self.content[:50]}..."

class Jjim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jjims')
    content_id = models.ForeignKey(TouristSpot, on_delete=models.CASCADE)
    jjim_on_off = models.BooleanField()

    class Meta:
        db_table = 'jjim'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '찜'
        verbose_name_plural = '찜 목록'
        unique_together = ['user', 'content_id']

    def __str__(self):
        return f"{self.user.first_name} - {self.content_id.title} - {'찜' if self.jjim_on_off else '찜 해제'}"

class MemberTrip(models.Model):
    TRIP_STATUS_CHOICES = [
        ('PLANNED', '계획됨'),
        ('COMPLETED', '완료됨'),
        ('RECOMMENDED', '추천됨'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_trips')
    status = models.CharField(max_length=20, choices=TRIP_STATUS_CHOICES)
    trip_title = models.CharField(max_length=100)
    travel_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'member_trip'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '회원 여행'
        verbose_name_plural = '회원 여행들'

    def __str__(self):
        return f"{self.user.first_name} - {self.trip_title}"

class MemberTripItinerary(models.Model):
    trip_id = models.ForeignKey(MemberTrip, on_delete=models.CASCADE)
    seq = models.SmallIntegerField()
    content_id = models.ForeignKey(TouristSpot, on_delete=models.CASCADE)
    visit_date = models.DateField(null=True, blank=True)
    stay_time = models.DurationField(null=True, blank=True)

    class Meta:
        db_table = 'member_trip_itinerary'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '여행 일정'
        verbose_name_plural = '여행 일정들'
        unique_together = ['trip_id', 'seq']

    def __str__(self):
        return f"{self.trip_id.trip_title} - {self.seq}번째"

# 기존 모델들 (호환성 유지를 위해 남겨둠)
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '찜 목록'
        verbose_name_plural = '찜 목록들'
        unique_together = ['user', 'destination']

    def __str__(self):
        return f"{self.user.first_name} - {self.destination.name}"

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
        return f"{self.user.first_name} - {self.title}"