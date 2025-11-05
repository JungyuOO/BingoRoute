import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone

from accounts.models import CustomUser
from service.models import MemberTrip, MemberTripItinerary, TouristSpot


class Command(BaseCommand):
    help = "샘플 여행 계획과 일정 데이터를 생성합니다."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding demo users"))
        users = [
            {
                "user_id": "demo_user1",
                "first_name": "홍길동",
                "email": "demo1@example.com",
            },
            {
                "user_id": "demo_user2",
                "first_name": "김철수",
                "email": "demo2@example.com",
            },
        ]

        created_users = []
        next_numeric_id = (CustomUser.objects.aggregate(max_id=Max("id")).get("max_id") or 0)

        for info in users:
            user = CustomUser.objects.filter(user_id=info["user_id"]).first()
            if user:
                created_users.append(user)
                continue

            next_numeric_id += 1
            temp_user_id = str(next_numeric_id)

            user = CustomUser(
                user_id=temp_user_id,
                username=info["user_id"],
                email=info["email"],
                first_name=info["first_name"],
                is_active=True,
            )
            user.set_password("password123!")
            user.save()

            CustomUser.objects.filter(pk=user.pk).update(
                user_id=info["user_id"],
                username=info["user_id"],
            )
            user.refresh_from_db()
            created_users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Users ready: {[u.user_id for u in created_users]}"))

        self.stdout.write(self.style.MIGRATE_HEADING("Selecting tourist spots"))
        available_spots = list(TouristSpot.objects.all()[:5])
        if len(available_spots) < 5:
            raise CommandError("tourist_spot 테이블에 최소 5개 이상의 데이터가 필요합니다.")
        self.stdout.write(
            self.style.SUCCESS(
                f"Using existing spots: {[spot.content_id for spot in available_spots]}"
            )
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding member trips"))
        base_date = timezone.now().date()
        trip_templates = [
            {
                "user_id": "demo_user1",
                "trip_title": "서울 도심 여행",
                "status": "PLANNED",
                "travel_date": base_date + datetime.timedelta(days=idx),
            }
            for idx in range(3)
        ] + [
            {
                "user_id": "demo_user2",
                "trip_title": "부산 힐링 여행",
                "status": "COMPLETED",
                "travel_date": base_date + datetime.timedelta(days=3),
            },
            {
                "user_id": "demo_user2",
                "trip_title": "제주 일출 투어",
                "status": "PLANNED",
                "travel_date": base_date + datetime.timedelta(days=7),
            },
        ]

        created_trips = []
        for template in trip_templates:
            trip, _ = MemberTrip.objects.update_or_create(
                user_id=template["user_id"],
                trip_title=template["trip_title"],
                defaults={
                    "status": template["status"],
                    "travel_date": template["travel_date"],
                },
            )
            created_trips.append(trip)
        self.stdout.write(self.style.SUCCESS(f"Created/updated {len(created_trips)} trips"))

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding itineraries"))
        all_spot_ids = [spot.content_id for spot in available_spots]
        for index, trip in enumerate(created_trips, start=1):
            for seq in (1, 2, 3):
                spot_id = all_spot_ids[(index + seq) % len(all_spot_ids)]
                MemberTripItinerary.objects.update_or_create(
                    trip_id=trip,
                    seq=seq,
                    defaults={
                        "content": TouristSpot.objects.get(content_id=spot_id),
                        "visit_date": trip.travel_date + datetime.timedelta(days=seq - 1),
                        "stay_time": datetime.timedelta(hours=2),
                    },
                )
        self.stdout.write(self.style.SUCCESS("Itineraries seeded"))

        self.stdout.write(self.style.SUCCESS("Demo data seeding completed."))
