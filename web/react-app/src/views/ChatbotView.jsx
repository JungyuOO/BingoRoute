import { useEffect, useState, useRef } from 'react'
import { ChatHeader, ChatMessage, QuickReplies, ChatInput } from '../components/features/chat'
import './ChatbotView.css'
import DestinationDetailModal from "../components/features/destinations/DestinationDetailModal";
const API_BASE = import.meta.env.VITE_API_BASE || '' // e.g., 'http://localhost:8000'


const INITIAL_CHIPS = [
  '역사와 문화 탐방',
  '쇼핑과 맛집 투어',
  '자연과 힐링',
  '핫플레이스 탐방',
  '전통 체험'
]

// 백엔드 관광지/날씨 API 연결 설정
const FALLBACK_IMAGE = 'https://placehold.co/300x200?text=No+Image'
// label: UI 문구, query: DB category_name 부분문자열, keywords: 입력 키워드
const CATEGORY_RULES = [
  { label: '역사와 문화 탐방', query: '고궁', keywords: ['역사', '문화', '고궁', '궁', '경복궁', '북촌', '한옥'] },
  { label: '쇼핑과 맛집 투어', query: '시장', keywords: ['쇼핑', '맛집', '시장', '명동', '남대문', '광장시장'] },
  { label: '자연과 힐링', query: '공원', keywords: ['자연', '힐링', '공원', '숲', '산책'] },
  { label: '핫플레이스 탐방', query: '문화거리', keywords: ['핫플', '핫플레이스', '성수', '연남', '한남'] },
  { label: '전통 체험', query: '체험', keywords: ['전통', '체험', '한복', '공예'] },
]

const systemGreeting = (
  <div className="system-greeting">
    <p>안녕하세요! 빙고루트 AI 여행 플래너입니다. ✨</p>
    <p>서울에서의 완벽한 여행 계획을 함께 세워보아요!</p>
    <p>어떤 스타일의 여행을 원하시나요?</p>
  </div>
)


  const detectCategory = (text) => {
    const t = (text || '').toLowerCase()
    return (
      CATEGORY_RULES.find((r) => r.keywords.some((k) => t.includes(k.toLowerCase())) ) || null
    )
  }

const shouldAskWeather = (text) => {
  const t = (text || '').toLowerCase()
  return ['날씨', '비', '우산', '기온', '온도', 'weather'].some((k) => t.includes(k))
}

const requestJson = async (url, options = {}) => {
  const res = await fetch(url, { credentials: 'include', ...options })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    const error = new Error(`HTTP ${res.status}`)
    error.responseText = text
    throw error
  }
  return res.json()
}

const fetchTouristSpots = async (categoryQuery) => {
  const params = new URLSearchParams()
  if (categoryQuery) params.append('category_name', categoryQuery)
  const data = await requestJson(`${API_BASE}/api/service/tourist_spots/${params.toString() ? `?${params}` : ''}`)
  return Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : []
}
  const fetchTouristSpotsFallback = async () => {
    // 백엔드 오류 대비: 무필터 조회 시도
    try {
      return await fetchTouristSpots()
    } catch (e) {
      console.error('tourist_spots fallback도 실패:', e)
      return []
    }
  }

const buildCards = (spots, intro) => {
  const cards = spots.slice(0, 8).map((s) => ({
    id: s.content_id,
    contentId: s.content_id,
    name: s.title,
    image: s.firstimage || s.firstimage2 || FALLBACK_IMAGE,
    desc: intro || (s.category_name || ''),
  }))
  return cards
}

// 상세 정보 보강 유틸
const toBool = (v) => {
  if (v === true) return true
  if (v === false) return false
  if (v == null) return false
  const s = String(v).trim().toLowerCase()
  if (!s) return false
  if (['0', 'n', 'no', 'false', '불가', '없음'].some(t => s === t || s.includes(t))) return false
  return ['1', 'y', 'yes', 'true', '가능', 'o', 'ok'].some(t => s === t || s.includes(t))
}

const fetchSpotDetail = async (contentId) => {
  const data = await requestJson(`${API_BASE}/api/service/tourist_spots/detail/${contentId}/`)
  return Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : []
}

const ChatbotView = () => {
  const [messages, setMessages] = useState([{ id: 1, role: 'assistant', content: systemGreeting }])
  const [chips, setChips] = useState(INITIAL_CHIPS)
  const [selectedDestination, setSelectedDestination] = useState(null)


  const pushMessage = (role, content, cards = null) => {
    const messageId = Date.now() + Math.random()
    setMessages((prev) => [...prev, { id: messageId, role, content, cards }])
  }

  // 상세 캐시
  const [detailCache, setDetailCache] = useState({})

  const handleCardClick = async (card) => {
    // 기본 카드 데이터로 먼저 모달 오픈
    const base = {
      ...card,
      tags: [],
      area: '',
      rating: '-',
      long: '',
      phone: '',
      closedDays: '',
      operatingHours: '',
      operatingSeason: '',
      parking: false,
      strollerFriendly: false,
      petFriendly: false,
      creditCard: false,
    }

    if (detailCache[card.contentId || card.id]) {
      setSelectedDestination(detailCache[card.contentId || card.id])
      return
    }
    setSelectedDestination(base)

    try {
      const list = await fetchSpotDetail(card.contentId || card.id)
      if (!Array.isArray(list) || list.length === 0) return

      const first = list[0]
      const tags = Array.from(new Set(list.map(d => d.info_name).filter(Boolean)))
      const infoTexts = list.map(d => (d.info_text || '').trim()).filter(Boolean)

      const enriched = {
        ...base,
        tags,
        area: first?.sigungu_name || base.area,
        long: infoTexts.length ? infoTexts.join('\n\n') : base.long,
        phone: first?.tel || base.phone,
        closedDays: first?.restdate || base.closedDays,
        operatingHours: first?.usetime || base.operatingHours,
        operatingSeason: first?.useseason || base.operatingSeason,
        parking: first?.is_parking != null ? toBool(first.is_parking) : base.parking,
        strollerFriendly: first?.is_baby_carriage != null ? toBool(first.is_baby_carriage) : base.strollerFriendly,
        petFriendly: first?.is_pet != null ? toBool(first.is_pet) : base.petFriendly,
        creditCard: first?.is_credit_card != null ? toBool(first.is_credit_card) : base.creditCard,
      }
      setDetailCache(prev => ({ ...prev, [card.contentId || card.id]: enriched }))
      setSelectedDestination(enriched)
    } catch (e) {
      console.error('detail fetch error', e)
    }
  }

  // 스크롤 기반 카드 컴포넌트
  const ScrollableCards = ({ cards, messageId }) => {
    const scrollContainerRef = useRef(null)
    const [canScrollLeft, setCanScrollLeft] = useState(false)
    const [canScrollRight, setCanScrollRight] = useState(true)

    const checkScrollButtons = () => {
      const container = scrollContainerRef.current
      if (container) {
        setCanScrollLeft(container.scrollLeft > 0)
        setCanScrollRight(
          container.scrollLeft < container.scrollWidth - container.clientWidth
        )
      }
    }

    const scrollLeft = () => {
      const container = scrollContainerRef.current
      if (container) {
        container.scrollBy({
          left: -300, // 카드 너비만큼 스크롤
          behavior: 'smooth'
        })
      }
    }

    const scrollRight = () => {
      const container = scrollContainerRef.current
      if (container) {
        container.scrollBy({
          left: 300, // 카드 너비만큼 스크롤
          behavior: 'smooth'
        })
      }
    }

    useEffect(() => {
      const container = scrollContainerRef.current
      if (container) {
        checkScrollButtons()
        container.addEventListener('scroll', checkScrollButtons)
        return () => container.removeEventListener('scroll', checkScrollButtons)
      }
    }, [])

    return (
      <div className="scrollable-cards-container">
        {canScrollLeft && (
          <button className="scroll-btn scroll-btn-left" onClick={scrollLeft}>
            ‹
          </button>
        )}
        
        <div 
          ref={scrollContainerRef}
          className="card-list-scrollable"
        >
          {cards.map((card) => (
            <div key={card.id} className="tour-card"
              onClick={() => handleCardClick(card)}
            >
              <img src={card.image} alt={card.name} className="tour-image" />
              <div className="tour-info">
                <h4>{card.name}</h4>
                <p>{card.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {canScrollRight && (
          <button className="scroll-btn scroll-btn-right" onClick={scrollRight}>
            ›
          </button>
        )}
      </div>
    )
  }

  const handleSend = async (text) => {
    const query = text.trim()
    if (!query) return
    pushMessage('user', <span>{query}</span>)

    const cat = detectCategory(query)
    const askWeather = shouldAskWeather(query)

    // 관광지: 카테고리 키워드가 있을 때만 조회
    if (cat) {
      try {
        let spots = []
        try {
          spots = await fetchTouristSpots(cat?.query)
        } catch (e) {
          console.error('tourist_spots 요청 실패:', e.responseText || e)
          spots = await fetchTouristSpotsFallback()
        }
        if (!spots.length && cat?.query) {
          // 카테고리 검색 결과가 비면 전체 조회 폴백
          spots = await fetchTouristSpots()
        }
        if (spots.length) {
          const intro =
            cat.label.includes('역사') ? '서울에서 역사와 문화를 느낄 수 있는 공간을 추천해드릴게요.' :
            cat.label.includes('핫플') ? '요즘 인기 있는 핫플레이스를 중심으로 일정을 제안드릴게요.' :
            cat.label.includes('자연') ? '도심 속에서 자연을 느낄 수 있는 힐링 스팟을 추천합니다.' :
            cat.label.includes('쇼핑') ? '쇼핑과 미식이 즐거운 코스로 여행지를 모아봤어요.' : cat.label
          pushMessage('assistant', <span>{intro}</span>)
          const cards = buildCards(spots, cat?.label)
          if (cards.length) pushMessage('cards', null, cards)
        } else {
          pushMessage('assistant', <span>관련된 관광지를 아직 찾지 못했어요. 다른 키워드로도 물어봐 주세요!</span>)
        }
      } catch (e) {
        console.error('관광지 로드 오류:', e.responseText || e)
        pushMessage('assistant', <span>관광지 정보를 불러올 수 없어요. 잠시 후 다시 시도해주세요.</span>)
      }
    }

    // 날씨
    if (askWeather) {
      try {
        const w = await requestJson(`${API_BASE}/api/weather/current/`)
        const summary = w?.summary || w?.data?.summary || '날씨 정보를 가져오지 못했어요.'
        pushMessage('assistant', <span>{summary}</span>)
      } catch (e) {
        pushMessage('assistant', <span>날씨 정보를 불러오는 중 오류가 발생했어요.</span>)
      }
    }
  }

  const handleChip = (label) => {
    handleSend(label)
    setChips([label, ...INITIAL_CHIPS.filter((c) => c !== label)].slice(0, 5))
  }

  useEffect(() => {
    document.title = 'AI 여행 플래너'
  }, [])

  return (
    <div className="br-container">
      <ChatHeader />

      <div className="section">
        <div className="chat-messages">
          {messages.map((m) => (
            m.role === 'cards' ? (
              <div key={m.id} className="cards-container">
                <ScrollableCards cards={m.cards} messageId={m.id} />
              </div>
            ) : (
              <ChatMessage key={m.id} role={m.role}>
                {m.content}
              </ChatMessage>
            )
          ))}
        </div>

        <div className="quick-replies-container">
          <QuickReplies options={chips} onSelect={handleChip} />
        </div>

        <ChatInput onSend={handleSend} />

        <div className="muted disclaimer">
          AI가 생성한 답변입니다. 실제 정보와 다를 수 있으니 참고용으로만 활용해주세요.
        </div>
        {/* ✅ 모달 추가 */}
        {selectedDestination && (
          <DestinationDetailModal
            destination={selectedDestination}
            isOpen={!!selectedDestination}
            onClose={() => setSelectedDestination(null)}
            isSaved={false}
            onToggleSave={() => console.log('찜하기 눌림')}
          />
        )}
      </div>
    </div>
  )
}

export default ChatbotView
