# JSON 직렬화

from rest_framework import serializers
from .models import TouristSpot, TouristDetail

# 관광지 직렬화기
class TouristSpotSerializer(serializers.ModelSerializer):
    # 지역 정보를 위해 첫 번째 상세 정보의 시군구명 가져오기
    area_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TouristSpot
        fields = '__all__'
    
    def get_area_name(self, obj):
        # 해당 관광지의 첫 번째 상세 정보에서 시군구명 가져오기
        from .models import TouristDetail
        detail = TouristDetail.objects.filter(content_id=obj.content_id).first()
        if detail and detail.sigungu_name:
            return detail.sigungu_name
        elif detail and detail.address:
            # 주소에서 구 정보 추출
            address_parts = detail.address.split(' ')
            if len(address_parts) >= 2:
                return address_parts[1]
        return obj.category_name or '정보없음'

# 관광지 상세 직렬화기
class TouristDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristDetail
        fields = '__all__'