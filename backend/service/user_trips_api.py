from rest_framework import generics
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import MemberTrip, MemberTripItinerary
from .serializers import UserTourPlanSerializer, UserTourItinerarySerializer

# 오류 처리용
from django.shortcuts import get_object_or_404

# 로그 설정
import logging
logger = logging.getLogger(__name__)


@extend_schema(
    tags=["여행계획"],
    summary="사용자 여행 계획 목록 조회",
    description="user_id, status 파라미터를 사용해 특정 사용자의 여행 계획을 필터링합니다.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            location=OpenApiParameter.QUERY,
            description="조회할 사용자 ID. 생략 시 전체 사용자의 여행 계획을 반환합니다.",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="status",
            location=OpenApiParameter.QUERY,
            description="여행 상태 필터 (예: PLANNED, COMPLETED).",
            required=False,
            type=str,
        ),
    ],
)
class UserTourPlanView(generics.ListAPIView):
    """회원별 여행 계획 목록을 조회하는 뷰"""

    serializer_class = UserTourPlanSerializer

    def get_queryset(self):
        qs = MemberTrip.objects.all().order_by("travel_date")
        user_id = self.request.query_params.get("user_id")
        status = self.request.query_params.get("status")

        if user_id:
            qs = qs.filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        return qs


@extend_schema(
    tags=["여행계획"],
    summary="여행 일정 조회",
    description="trip_id로 특정 여행 계획에 속한 관광지 일정을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="trip_id",
            location=OpenApiParameter.QUERY,
            description="필수. 조회할 여행 계획 ID.",
            required=True,
            type=int,
        ),
    ],
)

class UserTourItineraryView(generics.ListAPIView):
    """여행 계획에 속한 관광지 일정을 조회하는 뷰"""

    serializer_class = UserTourItinerarySerializer

    def get_queryset(self):
        trip_id = self.request.query_params.get("trip_id")
        if not trip_id:
            raise ValidationError({"trip_id": "여행 계획 ID(trip_id)는 필수 파라미터입니다."})

        qs = (
            MemberTripItinerary.objects.select_related("trip", "content")
            .filter(trip__trip_id=trip_id)
            .order_by("seq")
        )
        return qs


class UserTourPlanUpdateView(generics.UpdateAPIView):
    """여행 계획을 수정하는 뷰"""
    serializer_class = UserTourPlanSerializer

    def get_object(self):
        user_id = self.kwargs["user_id"]
        trip_id = self.kwargs["trip_id"]
        return get_object_or_404(MemberTrip, user_id=user_id, trip_id=trip_id)

    def perform_update(self, serializer):
        instance = serializer.instance or self.get_object()
        updates = serializer.validated_data

        changed = {
            field: (getattr(instance, field), value)
            for field, value in updates.items()
            if getattr(instance, field) != value
        }

        if changed:
            serializer.save()
            # 필요하면 여기서 로깅/추가 작업
            logger.info(f"UserTourPlan updated: {changed}")
        else:
            logger.info("No changes detected; update skipped.")



class UserTourItineraryUpdateView(generics.UpdateAPIView):
    """여행 계획에 속한 관광지를 수정하는 뷰"""

    serializer_class = UserTourItinerarySerializer
    queryset = MemberTripItinerary.objects.all()

    def get_object(self):
        trip_id = self.kwargs["trip_id"]
        seq = self.kwargs["seq"]
        return get_object_or_404(self.queryset, trip__trip_id=trip_id, seq=seq)
