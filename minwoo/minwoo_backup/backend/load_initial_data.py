import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingoroute_api.settings')
django.setup()

from destinations.models import Destination, DestinationTag

def load_destinations():
    destinations_data = [
        {
            'name': '경복궁',
            'area': '서울 종로구',
            'rating': 4.7,
            'duration': '2-3시간',
            'short_description': '조선의 대표 궁궐. 웅장한 건축과 아름다운 정원을 감상할 수 있어요.',
            'long_description': '경복궁은 1395년에 창건되어 조선왕조의 법궁으로 사용되었어요. 광화문, 근정전, 경회루 등 대표 명소가 많고 한복 체험과 함께 방문하면 더욱 특별한 추억을 만들 수 있어요.',
            'tags': ['궁궐', '역사', '문화']
        },
        {
            'name': '북촌한옥마을',
            'area': '서울 종로구',
            'rating': 4.6,
            'duration': '2-3시간',
            'short_description': '도심 속 고즈넉한 한옥 골목을 걸어보세요.',
            'long_description': '전통 한옥과 현대 문화가 공존하는 북촌은 사진 찍기 좋은 골목과 작은 갤러리가 곳곳에 있어 여유로운 산책 코스로 인기예요.',
            'tags': ['한옥', '산책', '사진']
        },
        {
            'name': '인사동',
            'area': '서울 종로구',
            'rating': 4.5,
            'duration': '2-3시간',
            'short_description': '전통 공예품과 맛있는 간식이 가득한 거리.',
            'long_description': '찻집, 공예품 상점, 갤러리, 길거리 간식까지 다양하게 즐길 수 있는 전통 거리예요. 주말엔 차 없는 거리로 운영돼 더욱 걷기 좋아요.',
            'tags': ['전통', '카페', '쇼핑']
        },
    ]

    for dest_data in destinations_data:
        tags = dest_data.pop('tags')
        destination, created = Destination.objects.get_or_create(
            name=dest_data['name'],
            defaults=dest_data
        )
        
        if created:
            for tag_name in tags:
                DestinationTag.objects.create(
                    destination=destination,
                    tag_name=tag_name
                )
            print(f"Created: {destination.name}")
        else:
            print(f"Already exists: {destination.name}")

if __name__ == '__main__':
    load_destinations()
    print("Initial data loading completed!")