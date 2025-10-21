from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import TouristSpot, TouristDetail
from .serializers import TouristSpotSerializer, TouristDetailSerializer

# optional : 카테고리별 필터
@extend_schema(
    tags = ["관광지"],
    summary="카테고리별 관광지 전체 조회",
    parameters=[
        OpenApiParameter(
            name='category_name',
            location=OpenApiParameter.QUERY,
            description='필터링할 카테고리 이름(예시:고궁, 생략 시 전체 조회)',
            required=False,
            type=str,
        )
    ]
)

# 카테고리별 관광지 전체 조회 API
class TouristSpotAllView(generics.ListAPIView):
    serializer_class = TouristSpotSerializer

    def get_queryset(self):
        qs = TouristSpot.objects.all().order_by("content_id")
        category = self.request.query_params.get("category_name")
        if category:
            qs = qs.filter(category_name=category)
        # 필요한 경우 복수 조건, 부분 일치 등을 여기서 처리
        return qs
    

@extend_schema(
    tags = ["관광지"],
    summary="관광지 상세 정보 조회",
)

class TouristSpotDetailView(generics.ListAPIView):
    serializer_class = TouristDetailSerializer

    def get_queryset(self):
        content_id = self.kwargs.get('content_id')
        base_queryset = TouristDetail.objects.all()
        if content_id is not None:
            base_queryset = base_queryset.filter(content_id=content_id)
        return base_queryset.order_by('content_id', 'info_name', 'id')
