import { useEffect, useState } from 'react'
import { ChatHeader, ChatMessage, QuickReplies, ChatInput } from '../components/features/chat'
import './ChatbotView.css'

const INITIAL_CHIPS = [
  '역사와 문화 탐방',
  '쇼핑과 맛집 투어',
  '자연과 힐링',
  '핫플레이스 탐방',
  '전통 체험'
]

// ⭐ 홈화면 추천 여행지 API 구조를 가정한 mock 데이터
// (나중에 API 응답 예시와 1:1로 맞출 수 있음)
const MOCK_DESTINATIONS = {
  history: [
    { id: 1, name: '경복궁', image: '/images/gyeongbokgung.jpg', desc: '조선의 대표 궁궐, 근정전과 경회루는 필수 코스!' },
    { id: 2, name: '북촌 한옥마을', image: '/images/bukchon.jpg', desc: '전통 한옥 거리와 한복 체험 스팟이 가득해요.' },
    { id: 3, name: '서촌', image: '/images/seochon.jpg', desc: '감성 카페와 전통 골목이 어우러진 힐링 명소.' },
    { id: 4, name: '덕수궁 돌담길', image: '/images/deoksu.jpg', desc: '도심 속 역사 산책로, 사진 명소로 유명해요.' }
  ],
  food: [
    { id: 1, name: '명동거리', image: '/images/myeongdong.jpg', desc: '쇼핑과 길거리 음식의 천국! 외국인 관광객 인기 No.1' },
    { id: 2, name: '남대문시장', image: '/images/namdaemun.jpg', desc: '서울 대표 재래시장, 볼거리와 먹거리 가득!' },
    { id: 3, name: '광장시장', image: '/images/gwangjang.jpg', desc: '빈대떡과 마약김밥으로 유명한 전통 시장.' },
    { id: 4, name: '홍대입구', image: '/images/hongdae.jpg', desc: '젊음의 거리, 예술과 맛집이 공존하는 핫플.' }
  ],
  nature: [
    { id: 1, name: '서울숲', image: '/images/seoulforest.jpg', desc: '도심 속 자연의 오아시스 🌳 사슴 먹이주기도 가능!' },
    { id: 2, name: '하늘공원', image: '/images/skypark.jpg', desc: '억새와 노을이 멋진 사진 명소.' },
    { id: 3, name: '북서울 꿈의숲', image: '/images/dreamforest.jpg', desc: '전망대와 산책 코스가 아름다운 힐링 명소.' },
    { id: 4, name: '뚝섬 한강공원', image: '/images/tteuksom.jpg', desc: '피크닉과 자전거 코스로 인기 많아요.' }
  ],
  hotplace: [
    { id: 1, name: '성수동', image: '/images/seongsu.jpg', desc: '리모델링 카페와 팝업스토어의 천국!' },
    { id: 2, name: '연남동', image: '/images/yeonnam.jpg', desc: '감성 카페거리와 예쁜 소품샵이 가득한 동네.' },
    { id: 3, name: '한남동', image: '/images/hannam.jpg', desc: '트렌디한 브랜드숍과 갤러리가 즐비한 곳.' },
    { id: 4, name: '익선동', image: '/images/ikseon.jpg', desc: '전통 한옥과 현대 감성이 어우러진 힙한 거리.' }
  ],
  tradition: [
    { id: 1, name: '인사동', image: '/images/insadong.jpg', desc: '전통 찻집과 공예 체험이 가능한 서울의 대표 거리.' },
    { id: 2, name: '남산골 한옥마을', image: '/images/namsangol.jpg', desc: '전통 공연과 한복 체험이 가능한 문화 공간.' },
    { id: 3, name: '국립고궁박물관', image: '/images/museum.jpg', desc: '조선 왕실의 유물과 전통문화를 전시.' },
    { id: 4, name: '한국의집', image: '/images/koreahouse.jpg', desc: '전통음식과 공연을 함께 즐길 수 있는 공간.' }
  ]
}

const systemGreeting = (
  <>
    <p style={{ margin: 0 }}>안녕하세요! 빙고루트 AI 여행 플래너입니다. ✨</p>
    <p style={{ margin: '6px 0 0 0' }}>서울에서의 완벽한 여행 계획을 함께 세워보아요!</p>
    <p style={{ margin: '6px 0 0 0' }}>어떤 스타일의 여행을 원하시나요?</p>
  </>
)

// ⭐ 수정된 mockReply (이제 카드 데이터도 함께 반환)
const mockReply = (text) => {
  if (text.includes('역사') || text.includes('문화')) {
    return {
      message: '경복궁, 북촌 한옥마을, 서촌 일대를 중심으로 코스를 추천해요. 📸 한복 대여와 사진 스팟도 함께 안내드릴게요!',
      cards: MOCK_DESTINATIONS.history
    }
  }
  if (text.includes('쇼핑') || text.includes('맛집')) {
    return {
      message: '명동-남대문-회현동 라인을 따라 쇼핑과 맛집을 함께 즐겨보세요. 🛍️ 비 오는 날에도 좋아요!',
      cards: MOCK_DESTINATIONS.food
    }
  }
  if (text.includes('자연') || text.includes('힐링')) {
    return {
      message: '서울숲-뚝섬 한강공원 코스로 여유로운 산책을 추천합니다. 🌿 카페와 피크닉 스팟도 함께 알려드릴게요.',
      cards: MOCK_DESTINATIONS.nature
    }
  }
  if (text.includes('핫플') || text.includes('핫플레이스')) {
    return {
      message: '성수-연남-한남 핫플 투어로 트렌디한 공간들을 둘러보는 코스를 짜드릴게요. 💫',
      cards: MOCK_DESTINATIONS.hotplace
    }
  }
  if (text.includes('전통')) {
    return {
      message: '인사동-익선동-낙원상가를 잇는 전통 체험 루트를 추천합니다. 🏮 공예 체험과 전통 다과 코스도 가능해요.',
      cards: MOCK_DESTINATIONS.tradition
    }
  }
  return {
    message: '좋아요! 선호하시는 기간과 동행, 예산을 알려주시면 맞춤 코스를 제안드릴게요.',
    cards: []
  }
}

const ChatbotView = () => {
  const [messages, setMessages] = useState([{ id: 1, role: 'assistant', content: systemGreeting }])
  const [chips, setChips] = useState(INITIAL_CHIPS)

  const pushMessage = (role, content) => {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), role, content }])
  }
  
  const handleSend = (text) => {
    pushMessage('user', <span>{text}</span>)
    const reply = mockReply(text) // ⭐ 추후 API 연결시 여기서부터 코드 수정

    // 1️⃣ 텍스트 응답
    setTimeout(() => {
      pushMessage('assistant', <span>{reply.message}</span>)

      // 2️⃣ 카드형 관광지 추천 추가
      if (reply.cards && reply.cards.length > 0) {
        pushMessage(
          'assistant',
          <div className="card-list">
            {reply.cards.map((card) => (
              <div key={card.id} className="tour-card">
                <img src={card.image} alt={card.name} className="tour-image" />
                <div className="tour-info">
                  <h4>{card.name}</h4>
                  <p>{card.desc}</p>
                </div>
              </div>
            ))}
          </div>
        )
      }
    }, 300)
  }

  const handleChip = (label) => {
    handleSend(label)
    setChips((prev) => [label, ...INITIAL_CHIPS.filter((c) => c !== label)].slice(0, 5))
  }

  useEffect(() => {
    document.title = 'AI 여행 플래너'
  }, [])

  return (
    <div className="br-container">
      <ChatHeader />

      <div className="section">
        <div style={{ minHeight: '46vh' }}>
          {messages.map((m) => (
            <ChatMessage key={m.id} role={m.role}>
              {m.content}
            </ChatMessage>
          ))}
        </div>

        <div style={{ margin: '8px 0 16px' }}>
          <QuickReplies options={chips} onSelect={handleChip} />
        </div>

        <ChatInput onSend={handleSend} />

        <div className="muted" style={{ fontSize: 15, marginTop: 8 }}>
          AI가 생성한 답변입니다. 실제 정보와 다를 수 있으니 참고용으로만 활용해주세요.
        </div>
      </div>
    </div>
  )
}

export default ChatbotView
