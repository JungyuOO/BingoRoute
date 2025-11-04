from rest_framework import generics
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import MemberTrip, MemberTripItinerary
from .serializers import (
    UserTourPlanReadSerializer,
    UserTourPlanCreateSerializer,
    UserTourPlanUpdateSerializer,
    UserTourItineraryReadSerializer,
    UserTourItineraryCreateSerializer,
    UserTourItineraryUpdateSerializer,
)

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

import logging
logger = logging.getLogger(__name__)


@extend_schema(
    tags=["여행계획"],
    summary="유저별 여행 계획 조회(목록/단건) 및 생성",
    description=(
        "user_id는 필수입니다. GET은 user_id 기준으로 전체 목록을 반환하며, 선택적으로 trip_id를 전달하면 단건 조회로 동작합니다. "
        "POST는 새로운 여행 계획을 생성합니다."
    ),
    parameters=[
        OpenApiParameter(
            name="user_id",
            location=OpenApiParameter.QUERY,
            description="필수. 조회할 사용자 ID.",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="status",
            location=OpenApiParameter.QUERY,
            description="여행 상태 필터 (예: PLANNED, COMPLETED, RECOMMENDED).",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="trip_id",
            location=OpenApiParameter.QUERY,
            description="선택. 특정 여행 계획 ID를 전달하면 단건 조회 합니다.",
            required=False,
            type=int,
        ),
    ],
)
class UserTourPlanView(generics.ListCreateAPIView):
    """회원별 여행 계획 목록/단건 조회 및 생성"""

    serializer_class = UserTourPlanReadSerializer

    def get_queryset(self):
        itinerary_prefetch = Prefetch(
            "itinerary_set",
            queryset=MemberTripItinerary.objects.order_by("seq"),
        )
        qs = (
            MemberTrip.objects.all()
            .prefetch_related(itinerary_prefetch)
            .order_by("travel_date")
        )
        user_id = self.request.query_params.get("user_id")
        status = self.request.query_params.get("status")
        trip_id = self.request.query_params.get("trip_id")

        if not user_id:
            raise ValidationError({"user_id": "user_id는 필수 파라미터입니다."})

        qs = qs.filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        if trip_id:
            qs = qs.filter(trip_id=trip_id)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserTourPlanCreateSerializer
        return UserTourPlanReadSerializer

    @extend_schema(
        tags=["여행계획"],
        request=UserTourPlanCreateSerializer,
        responses={201: UserTourPlanReadSerializer},
        description="새로운 여행 계획을 생성합니다.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user_id = self.request.query_params.get("user_id")
        if not user_id:
            raise ValidationError({"user_id": "user_id는 필수입니다."})
        serializer.context['user_id'] = user_id
        instance = serializer.save()
        logger.info("UserTourPlan created: trip_id=%s user_id=%s", instance.trip_id, instance.user_id)


@extend_schema(
    tags=["여행별 관광지"],
    summary="여행별 관광지 목록 조회 및 생성",
    description="trip_id는 필수입니다. GET은 trip_id 기준으로 해당 여행의 모든 일정 목록을 반환하며, POST는 새로운 일정(관광지)을 추가합니다.",
    parameters=[
        OpenApiParameter(
            name="trip_id",
            location=OpenApiParameter.QUERY,
            description="필수. 일정 목록을 조회할 여행 계획 ID.",
            required=True,
            type=int,
        ),
    ],
)
class UserTourItineraryView(generics.ListCreateAPIView):
    """여행별 관광지 일정 조회 및 생성"""

    serializer_class = UserTourItineraryReadSerializer

    def get_queryset(self):
        trip_id = self.request.query_params.get("trip_id")
        if not trip_id:
            raise ValidationError({"trip_id": "trip_id는 필수 파라미터입니다."})
        return (
            MemberTripItinerary.objects.select_related("trip_id", "content")
            .filter(trip_id=trip_id)
            .order_by("seq")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserTourItineraryCreateSerializer
        return UserTourItineraryReadSerializer

    @extend_schema(
        tags=["여행별 관광지"],
        request=UserTourItineraryCreateSerializer,
        responses={201: UserTourItineraryReadSerializer},
        description="특정 여행에 새로운 일정(관광지)을 추가합니다. trip_id, content_id, seq는 필수입니다.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        trip_id = self.request.query_params.get("trip_id")
        if trip_id is None:
            raise ValidationError({"trip_id": "trip_id는 필수입니다."})
        serializer.context['trip_id'] = trip_id
        instance = serializer.save()
        logger.info(
            "UserTourItinerary created: itinerary_id=%s trip_id=%s seq=%s",
            instance.itinerary_id,
            instance.trip_id_id,
            instance.seq,
        )


@extend_schema(
    tags=["여행계획"],
    summary="여행 계획 단건 조회/수정/삭제",
    description="user_id와 trip_id 조합으로 특정 여행 계획을 조회/수정/삭제합니다.",
)
class UserTourPlanManageView(generics.RetrieveUpdateDestroyAPIView):
    """여행 계획 단건 조회/수정/삭제"""

    serializer_class = UserTourPlanReadSerializer
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        trip_id = self.kwargs["trip_id"]
        return get_object_or_404(MemberTrip, user_id=user_id, trip_id=trip_id)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserTourPlanUpdateSerializer
        return UserTourPlanReadSerializer

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


@extend_schema(
    tags=["여행별 관광지"],
    summary="여행별 관광지 단건 조회/수정/삭제",
    description="itinerary_id를 이용해 특정 일정을 조회/수정/삭제합니다.",
)
class UserTourItineraryManageView(generics.RetrieveUpdateDestroyAPIView):
    """여행 계획에 속한 관광지 단건 조회/수정/삭제"""

    serializer_class = UserTourItineraryReadSerializer
    queryset = MemberTripItinerary.objects.select_related("trip_id", "content").all()
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        itinerary_id = self.kwargs["itinerary_id"]
        return get_object_or_404(self.queryset, itinerary_id=itinerary_id)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserTourItineraryUpdateSerializer
        return UserTourItineraryReadSerializer

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
                "UserTourItinerary updated: itinerary_id=%s changes=%s",
                instance.itinerary_id,
                changed,
            )
        else:
            logger.info(
                "No changes detected; itinerary update skipped (itinerary_id=%s)",
                instance.itinerary_id,
            )

    def perform_destroy(self, instance):
        logger.info("UserTourItinerary deleted: itinerary_id=%s", instance.itinerary_id)
        instance.delete()
