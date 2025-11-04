# JSON 직렬화

from django.db import transaction
from django.db.models import F, Max
from rest_framework import serializers

from .models import TouristSpot, TouristDetail, MemberTrip, MemberTripItinerary, Jjim

# 관광지 직렬화기
class TouristSpotSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()

    class Meta:
        model = TouristSpot
        fields = [
            'content_id',
            'title',
            'firstimage',
            'firstimage2',
            'category_code',
            'category_name',
            'area',
        ]

    def get_area(self, obj):
        return (
            getattr(obj, 'detail_sigungu', None)
            or getattr(obj, 'detail_address', None)
            or ''
        )

# 관광지 상세 직렬화기
class TouristDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristDetail
        fields = '__all__'

def _generate_title(user_id: str) -> str:
    count = MemberTrip.objects.filter(user_id=user_id).count() + 1
    return f"untitled-{count}"


class UserTourItineraryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTripItinerary
        fields = ['itinerary_id', 'trip_id', 'seq', 'content_id', 'visit_date', 'stay_time']


class UserTourPlanReadSerializer(serializers.ModelSerializer):
    itineraries = UserTourItineraryReadSerializer(
        many=True,
        source='itinerary_set',
        read_only=True,
    )

    class Meta:
        model = MemberTrip
        fields = [
            'trip_id',
            'user_id',
            'status',
            'trip_title',
            'travel_date',
            'created_at',
            'updated_at',
            'itineraries',
        ]


class UserTourPlanItineraryInputSerializer(serializers.Serializer):
    seq = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="여행지 순서를 직접 지정할 수 있습니다. 지정하지 않으면 입력된 순서대로 저장됩니다.",
        style={'example': 1},
    )
    content_id = serializers.SlugRelatedField(
        source='content',
        slug_field='content_id',
        queryset=TouristSpot.objects.all(),
        help_text="추가할 첫 여행지의 content_id (예: 'A1234567').",
        style={'example': 'A1234567'},
    )
    visit_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="방문 예정일 (예: '2025-11-04').",
        style={'example': '2025-11-04'},
    )
    stay_time = serializers.DurationField(
        required=False,
        allow_null=True,
        help_text="머무를 예상 시간. 예: '05:00:00'(5시간), '1 00:00:00'(1일).",
        style={'example': '05:00:00'},
    )


class UserTourPlanCreateSerializer(serializers.ModelSerializer):
    itineraries = UserTourPlanItineraryInputSerializer(
        many=True,
        write_only=True,
        required=False,
        help_text="신규 여행 계획에 포함할 일정 목록입니다. 제공된 순서대로 저장됩니다.",
    )

    class Meta:
        model = MemberTrip
        fields = ['status', 'trip_title', 'travel_date', 'itineraries']

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        if not user_id:
            raise serializers.ValidationError({"user_id": "user_id is required"})
        title = validated_data.get('trip_title')
        if not title:
            validated_data['trip_title'] = _generate_title(user_id)
        itineraries_data = validated_data.pop('itineraries', [])

        with transaction.atomic():
            trip = MemberTrip.objects.create(user_id=user_id, **validated_data)

            if itineraries_data:
                entries = [
                    MemberTripItinerary(
                        trip_id=trip,
                        seq=itinerary.get('seq') or index,
                        content=itinerary['content'],
                        visit_date=itinerary.get('visit_date'),
                        stay_time=itinerary.get('stay_time'),
                    )
                    for index, itinerary in enumerate(itineraries_data, start=1)
                ]
                MemberTripItinerary.objects.bulk_create(entries)

        return trip


class UserTourPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTrip
        fields = ['status', 'trip_title', 'travel_date']

    def update(self, instance, validated_data):
        title = validated_data.get('trip_title')
        if title == '':
            validated_data['trip_title'] = _generate_title(instance.user_id)
        return super().update(instance, validated_data)


class UserTourItineraryCreateSerializer(serializers.ModelSerializer):
    seq = serializers.IntegerField(read_only=True)
    content_id = serializers.SlugRelatedField(
        source='content',
        slug_field='content_id',
        queryset=TouristSpot.objects.all(),
        help_text="추가할 관광지의 content_id (예: 'A1234567').",
        style={'example': 'A1234567'},
    )
    visit_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="방문 예정일 (예: '2025-11-04').",
        style={'example': '2025-11-04'},
    )
    stay_time = serializers.DurationField(
        required=False,
        allow_null=True,
        help_text="머무를 예상 시간. 예: '05:00:00'(5시간), '1 00:00:00'(1일), 'PT5H'(ISO 8601).",
        style={'example': '05:00:00'},
    )

    class Meta:
        model = MemberTripItinerary
        fields = ['seq', 'content_id', 'visit_date', 'stay_time']

    def create(self, validated_data):
        trip_id = self.context.get('trip_id')
        if trip_id is None:
            raise serializers.ValidationError({"trip_id": "trip_id is required"})

        last_seq = (
            MemberTripItinerary.objects
            .filter(trip_id_id=trip_id)
            .aggregate(max_seq=Max('seq'))
            .get('max_seq') or 0
        )
        validated_data['seq'] = last_seq + 1
        return MemberTripItinerary.objects.create(trip_id_id=trip_id, **validated_data)


class UserTourItineraryUpdateSerializer(serializers.ModelSerializer):
    content_id = serializers.SlugRelatedField(
        source='content',
        slug_field='content_id',
        queryset=TouristSpot.objects.all(),
        help_text="변경할 관광지의 content_id (예: 'A1234567').",
        style={'example': 'A1234567'},
    )
    visit_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="방문 예정일 (예: '2025-11-04').",
        style={'example': '2025-11-04'},
    )
    stay_time = serializers.DurationField(
        required=False,
        allow_null=True,
        help_text="머무를 예상 시간. 예: '05:00:00'(5시간), '1 00:00:00'(1일), 'PT5H'(ISO 8601).",
        style={'example': '05:00:00'},
    )

    class Meta:
        model = MemberTripItinerary
        fields = ['seq', 'content_id', 'visit_date', 'stay_time']

    def update(self, instance, validated_data):
        trip_id = instance.trip_id_id
        current_seq = instance.seq
        new_seq = validated_data.pop('seq', current_seq)

        if self.partial and 'content' not in validated_data:
            raise serializers.ValidationError({"content_id": "content_id is required for partial updates."})

        with transaction.atomic():
            max_seq = (
                MemberTripItinerary.objects
                .filter(trip_id_id=trip_id)
                .exclude(pk=instance.pk)
                .aggregate(max_seq=Max('seq'))
                .get('max_seq') or 0
            )
            new_seq = max(1, min(new_seq, max_seq + 1))

            if new_seq != current_seq:
                MemberTripItinerary.objects.filter(pk=instance.pk).update(seq=0)
                if new_seq < current_seq:
                    MemberTripItinerary.objects.filter(
                        trip_id_id=trip_id,
                        seq__gte=new_seq,
                        seq__lt=current_seq,
                    ).update(seq=F('seq') + 1)
                else:
                    MemberTripItinerary.objects.filter(
                        trip_id_id=trip_id,
                        seq__gt=current_seq,
                        seq__lte=new_seq,
                    ).update(seq=F('seq') - 1)
                MemberTripItinerary.objects.filter(pk=instance.pk).update(seq=new_seq)
                instance.seq = new_seq

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            instance.refresh_from_db()
        return instance


class JjimSerializer(serializers.ModelSerializer):
    content_id = serializers.CharField(read_only=True)

    class Meta:
        model = Jjim
        fields = ('content_id',)


class JjimCreateSerializer(serializers.ModelSerializer):
    content_id = serializers.SlugRelatedField(
        source='content',
        slug_field='content_id',
        queryset=TouristSpot.objects.all(),
    )

    class Meta:
        model = Jjim
        fields = ('user_id', 'content_id')

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        content = attrs.get('content')
        if user_id and content and Jjim.objects.filter(user_id=user_id, content=content).exists():
            raise serializers.ValidationError("이미 찜한 관광지입니다.")
        return attrs


class JjimDeleteSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    content_id = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        content_id = attrs.get('content_id')
        if not Jjim.objects.filter(user_id=user_id, content_id=content_id).exists():
            raise serializers.ValidationError("삭제할 찜 정보가 존재하지 않습니다.")
        return attrs
