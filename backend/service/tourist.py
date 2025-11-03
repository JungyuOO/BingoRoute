from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from .models import TouristSpot, TouristDetail
from .serializers import TouristSpotSerializer, TouristDetailSerializer
from destinations.models import Jjim
from .serializers import (
    JjimCreateSerializer,
    JjimDeleteSerializer,
    JjimSerializer,
)

# optional : 카테고리/관광지ID 필터
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
        ),
        OpenApiParameter(
            name='content_id',
            location=OpenApiParameter.QUERY,
            description='필터링할 관광지 ID',
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
        content =  self.request.query_params.get("content_id")
        if content:
            qs = qs.filter(content_id=content)
        if category:
            # 부분 일치로도 검색되도록 변경
            qs = qs.filter(category_name__icontains=category)
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


class UserJjimView(generics.GenericAPIView):
    """사용자 찜 목록 조회, 추가, 삭제를 담당하는 뷰"""
    serializer_class = JjimCreateSerializer

    @staticmethod
    def _get_payload(request):
        """요청 본문이 없으면 쿼리 파라미터에서 user_id, content_id를 읽어온다."""
        data = request.data if request.data else request.query_params
        if hasattr(data, "dict"):
            data = data.dict()
        return data

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if not user_id:
            return Jjim.objects.none()
        return Jjim.objects.filter(user__user_id=user_id, jjim_on_off=True).order_by("content_id")

    @extend_schema(
        tags=["찜하기"],
        summary="사용자 찜 목록 조회",
        description="user_id를 받아 해당 사용자의 찜한 관광지 content_id 목록을 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.QUERY,
                description="조회할 사용자 ID.",
                required=True,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            raise ValidationError({"user_id": "찜 목록을 조회하려면 user_id가 필요합니다."})
        
        queryset = self.get_queryset()
        content_ids = list(queryset.values_list("content_id__content_id", flat=True))
        return Response({"content_id": content_ids})

    @extend_schema(
        tags=["찜하기"],
        summary="관광지 찜 추가",
        description="user_id와 content_id를 받아 찜 테이블에 저장합니다.",
        request=JjimCreateSerializer,
        responses={201: JjimSerializer},
        parameters=[
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.QUERY,
                description="필수. 찜을 등록할 사용자 ID.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="content_id",
                location=OpenApiParameter.QUERY,
                description="필수. 찜할 관광지 ID.",
                required=True,
                type=str,
            ),
        ],
        examples=[
            OpenApiExample(
                name="찜 추가 예시",
                description="사용자 gyulteng2가 content_id 2733967을 찜한 경우",
                value={"user_id": "gyulteng2", "content_id": "2733967"},
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        payload = self._get_payload(request)
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        jjim = serializer.save()
        return Response(JjimSerializer(jjim).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["찜하기"],
        description="user_id와 content_id를 받아 해당 찜 데이터를 삭제합니다.",
        summary="관광지 찜 해제",
        request=JjimDeleteSerializer,
        responses={204: None},
        parameters=[
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.QUERY,
                description="찜을 해제할 사용자 ID.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="content_id",
                location=OpenApiParameter.QUERY,
                description="해제할 관광지 ID.",
                required=True,
                type=str,
            ),
        ],
        examples=[
            OpenApiExample(
                name="찜 해제 예시",
                description="사용자 gyulteng2가 content_id 2733967 찜을 해제하는 경우",
                value={"user_id": "gyulteng2", "content_id": "2733967"},
            ),
        ],
    )
    def delete(self, request, *args, **kwargs):
        payload = self._get_payload(request)
        serializer = JjimDeleteSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data["user_id"]
        content_id = serializer.validated_data["content_id"]
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"user_id": "존재하지 않는 사용자입니다."})
        
        try:
            tourist_spot = TouristSpot.objects.get(content_id=content_id)
        except TouristSpot.DoesNotExist:
            raise ValidationError({"content_id": "존재하지 않는 관광지입니다."})
        
        # jjim_on_off를 False로 업데이트 (완전 삭제 대신)
        updated = Jjim.objects.filter(
            user=user, 
            content_id=tourist_spot
        ).update(jjim_on_off=False)
        
        if updated == 0:
            raise NotFound("삭제할 찜 정보가 존재하지 않습니다.")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
