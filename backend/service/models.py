from django.db import models
from pgvector.django import VectorField
# DB 테이블 접근
# Create your models here.

# 관광지 테이블
class TouristSpot(models.Model):
    content_id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=200)
    firstimage = models.CharField(max_length=500, null=True, blank=True)
    firstimage2 = models.CharField(max_length=500, null=True, blank=True)
    category_code = models.CharField(max_length=20, null=True, blank=True)
    category_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tourist_spot'
        managed = False

# 관광지 상세 정보 테이블
class TouristDetail(models.Model):
    id = models.AutoField(primary_key=True)
    content_id = models.CharField(max_length=20)
    address_code = models.CharField(max_length=20, null=True, blank=True)
    sigungu_name = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    map_x = models.FloatField(null=True, blank=True)
    map_y = models.FloatField(null=True, blank=True)
    intro_serial_num = models.CharField(max_length=50, null=True, blank=True)
    content_type_id = models.CharField(max_length=20, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    useseason = models.CharField(max_length=500, null=True, blank=True)
    usetime = models.CharField(max_length=500, null=True, blank=True)
    is_parking = models.CharField(max_length=20, null=True, blank=True)
    is_baby_carriage = models.CharField(max_length=20, null=True, blank=True)
    is_pet = models.CharField(max_length=20, null=True, blank=True)
    is_credit_card = models.CharField(max_length=20, null=True, blank=True)
    info_serial_num = models.CharField(max_length=50, null=True, blank=True)
    info_name = models.CharField(max_length=200, null=True, blank=True)
    info_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.content_id} - {self.info_name or ""}'

    class Meta:
        db_table = 'tourist_spot_detail'
        managed = False
        ordering = ['content_id', 'info_name', 'id']
        unique_together = (('content_id', 'info_name'),)

# 회원별 여행 목록 테이블
class MemberTrip(models.Model):
    TRIP_STATUS_CHOICES = [
        ('PLANNED', '계획됨'),
        ('COMPLETED', '완료됨'),
        ('RECOMMENDED', '추천됨'),
    ]

    trip_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=TRIP_STATUS_CHOICES)
    trip_title = models.CharField(max_length=200)
    travel_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip_title

    class Meta:
        db_table = 'member_trip'
        managed = False
        ordering = ['travel_date']


# 여행별 관광지(여행 일정) 테이블
class MemberTripItinerary(models.Model):
    itinerary_id = models.BigAutoField(primary_key=True)
    trip_id = models.ForeignKey(
        MemberTrip,
        db_column='trip_id',
        related_name='itinerary_set',
        on_delete=models.CASCADE,
    )
    seq = models.SmallIntegerField()
    content = models.ForeignKey(
        TouristSpot,
        db_column='content_id',
        to_field='content_id',
        on_delete=models.CASCADE,
    )
    visit_date = models.DateField(null=True, blank=True)
    stay_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f'{self.trip_id.trip_title} - {self.content.title}'

    class Meta:
        db_table = 'member_trip_itinerary'
        managed = False
        ordering = ['trip_id', 'seq']
        unique_together = ('trip_id', 'seq')

# 찜 테이블
class Jjim(models.Model):
    jjim_id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=50)
    content = models.ForeignKey(
        TouristSpot,
        db_column='content_id',
        to_field='content_id',
        on_delete=models.CASCADE,
        related_name='jjim_entries',
    )

    class Meta:
        db_table = 'jjim'
        managed = False  # Django가 이 테이블을 관리하지 않음
        verbose_name = '찜'
        verbose_name_plural = '찜 목록'
        unique_together = ('user_id', 'content')

    def __str__(self):
        return f"{self.user_id} - {self.content.title}"

# RAG 벡터 테이블
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
