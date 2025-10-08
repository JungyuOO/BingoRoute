export const DESTINATIONS = [
  {
    id: 'gyeongbokgung',
    name: '경복궁',
    area: '서울 종로구',
    rating: 4.7,
    duration: '2-3시간',
    tags: ['궁궐', '역사', '문화'],
    short: '조선의 대표 궁궐. 웅장한 건축과 아름다운 정원을 감상할 수 있어요.',
    long: '경복궁은 1395년에 창건되어 조선왕조의 법궁으로 사용되었어요. 광화문, 근정전, 경회루 등 대표 명소가 많고 한복 체험과 함께 방문하면 더욱 특별한 추억을 만들 수 있어요.',
    image: null,
  },
  {
    id: 'bukchon',
    name: '북촌한옥마을',
    area: '서울 종로구',
    rating: 4.6,
    duration: '2-3시간',
    tags: ['한옥', '산책', '사진'],
    short: '도심 속 고즈넉한 한옥 골목을 걸어보세요.',
    long: '전통 한옥과 현대 문화가 공존하는 북촌은 사진 찍기 좋은 골목과 작은 갤러리가 곳곳에 있어 여유로운 산책 코스로 인기예요.',
    image: null,
  },
  {
    id: 'insadong',
    name: '인사동',
    area: '서울 종로구',
    rating: 4.5,
    duration: '2-3시간',
    tags: ['전통', '카페', '쇼핑'],
    short: '전통 공예품과 맛있는 간식이 가득한 거리.',
    long: '찻집, 공예품 상점, 갤러리, 길거리 간식까지 다양하게 즐길 수 있는 전통 거리예요. 주말엔 차 없는 거리로 운영돼 더욱 걷기 좋아요.',
    image: null,
  },
];

export const WEATHER_PRESETS = {
  '서울': { temp: 18, humidity: 46, wind: '2.3 m/s', sky: '맑음', advice: '얇은 겉옷과 편한 신발 추천 👟' },
  '부산': { temp: 21, humidity: 52, wind: '3.1 m/s', sky: '구름 조금', advice: '바닷바람이 선선해요. 모자 챙기기 🧢' },
  '제주': { temp: 20, humidity: 58, wind: '5.2 m/s', sky: '바람 강함', advice: '바람막이 필수! 🌬️' },
};