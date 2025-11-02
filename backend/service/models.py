from django.db import models
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

# 관
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
