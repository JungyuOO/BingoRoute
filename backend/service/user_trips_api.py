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
    summary="사용자 여행 계획 목록 조회/생성",
    description="user_id, status 파라미터로 특정 사용자의 여행 계획을 필터링하거나 새로운 여행 계획을 생성합니다.",
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
class UserTourPlanView(generics.ListCreateAPIView):
    """회원별 여행 계획 목록 조회/생성"""

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
        request=UserTourPlanSerializer,
        responses={201: UserTourPlanSerializer},
        description="새로운 여행 계획을 생성합니다.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info("UserTourPlan created: trip_id=%s user_id=%s", instance.trip_id, instance.user_id)


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
            .filter(trip_id=trip_id)
            .order_by("seq")
        )
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

class UserTourPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """여행 계획 단건 조회/수정/삭제"""
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
            logger.info("UserTourPlan updated: trip_id=%s changes=%s", instance.trip_id, changed)
        else:
            logger.info("No changes detected; update skipped for trip_id=%s", instance.trip_id)

    def perform_destroy(self, instance):
        logger.info("UserTourPlan deleted: trip_id=%s user_id=%s", instance.trip_id, instance.user_id)
        instance.delete()



class UserTourItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """여행 계획에 속한 관광지 단건 조회/수정/삭제"""

    serializer_class = UserTourItinerarySerializer
    queryset = MemberTripItinerary.objects.all()

    def get_object(self):
        trip_id = self.kwargs["trip_id"]
        seq = self.kwargs["seq"]
        return get_object_or_404(self.queryset, trip_id=trip_id, seq=seq)

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
            logger.info(
                "UserTourItinerary updated: trip_id=%s seq=%s changes=%s",
                instance.trip_id_id,
                instance.seq,
                changed,
            )
        else:
            logger.info(
                "No changes detected; itinerary update skipped (trip_id=%s, seq=%s)",
                instance.trip_id_id,
                instance.seq,
            )

    def perform_destroy(self, instance):
        logger.info("UserTourItinerary deleted: trip_id=%s seq=%s", instance.trip_id_id, instance.seq)
        instance.delete()
