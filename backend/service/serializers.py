# JSON 직렬화

from rest_framework import serializers
from .models import TouristSpot, TouristDetail
from destinations.models import Jjim

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


# 찜하기 관련 직렬화기
class JjimSerializer(serializers.ModelSerializer):
    content_id_value = serializers.CharField(source='content_id.content_id', read_only=True)
    
    class Meta:
        model = Jjim
        fields = ['user', 'content_id', 'content_id_value', 'jjim_on_off']


class JjimCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=50, help_text="찜을 등록할 사용자 ID")
    content_id = serializers.CharField(max_length=20, help_text="찜할 관광지 ID")
    
    def validate_content_id(self, value):
        """관광지가 존재하는지 확인"""
        if not TouristSpot.objects.filter(content_id=value).exists():
            raise serializers.ValidationError("존재하지 않는 관광지입니다.")
        return value
    
    def save(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_id = self.validated_data['user_id']
        content_id = self.validated_data['content_id']
        
        # 사용자 확인
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "존재하지 않는 사용자입니다."})
        
        # 관광지 객체 가져오기
        tourist_spot = TouristSpot.objects.get(content_id=content_id)
        
        # 이미 찜한 경우 jjim_on_off를 True로 업데이트, 없으면 생성
        jjim, created = Jjim.objects.update_or_create(
            user=user,
            content_id=tourist_spot,
            defaults={'jjim_on_off': True}
        )
        
        return jjim


class JjimDeleteSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=50, help_text="찜을 해제할 사용자 ID")
    content_id = serializers.CharField(max_length=20, help_text="해제할 관광지 ID")