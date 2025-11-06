import { useEffect, useState, useRef, useCallback } from 'react'
import { ChatHeader, ChatMessage, QuickReplies, ChatInput } from '../components/features/chat'
import './ChatbotView.css'
import DestinationDetailModal from "../components/features/destinations/DestinationDetailModal";
import { fetchTouristSpotDetail, normalizeTouristSpot } from '../services/touristService'
// 백엔드 API 기본 주소: .env의 VITE_API_BASE가 없으면 로컬 백엔드로 기본
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'


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
  return spots
    .slice(0, 8)
    .map((spot) => {
      const normalized = normalizeTouristSpot(spot)
      if (!normalized) return null
      return {
        ...normalized,
        contentId: normalized.id,
        image: normalized.image || FALLBACK_IMAGE,
        previewText: intro || normalized.short,
      }
    })
    .filter(Boolean)
}

const formatWeatherSummary = (payload) => {
  if (!payload) return null

  if (typeof payload.summary === 'string' && payload.summary.trim()) {
    return payload.summary.trim()
  }

  const data = payload.data || null
  if (!data || !data.regions || typeof data.regions !== 'object') return null

  const [regionName, regionData] = Object.entries(data.regions).find(([, info]) => info && Object.keys(info).length) || []
  if (!regionName || !regionData) return null

  const temperature = regionData.temperature ?? regionData.temp ?? '정보 없음'
  const wind = regionData.wind_speed ?? regionData.wind ?? '정보 없음'
  const rainfallRaw = regionData.precipitation ?? regionData.rainfall ?? '정보 없음'
  const rainfall = rainfallRaw === '0' ? '강수 없음' : rainfallRaw
  const advice = regionData.advice

  const timestampLabel = [data.display_date, data.display_time].filter(Boolean).join(' ')
  const parts = []
  if (timestampLabel) parts.push(`${timestampLabel} 기준`)
  parts.push(`${regionName} 기온 ${temperature}`)
  if (wind && wind !== '정보 없음' && wind !== '정보없음') parts.push(`풍속 ${wind}`)
  if (rainfall && rainfall !== '정보 없음' && rainfall !== '정보없음') parts.push(`강수량 ${rainfall}`)

  const summary = `${parts.join(', ')}.` + (advice ? ` ${advice}` : '')
  return summary.trim()
}

const ChatbotView = () => {
  const [messages, setMessages] = useState([{ id: 1, role: 'assistant', content: systemGreeting }])
  const [chips, setChips] = useState(INITIAL_CHIPS)
  const [selectedDestination, setSelectedDestination] = useState(null)
  const [destinationDetail, setDestinationDetail] = useState(null)
  const [destinationDetailLoading, setDestinationDetailLoading] = useState(false)
  const [destinationDetailError, setDestinationDetailError] = useState(null)

  const activeDetailIdRef = useRef(null)
  const pushMessage = (role, content, cards = null) => {
    const messageId = Date.now() + Math.random()
    setMessages((prev) => [...prev, { id: messageId, role, content, cards }])
  }

  // 상세 캐시
  const [detailCache, setDetailCache] = useState({})

  const loadDestinationDetail = useCallback(async (contentId) => {
    if (!contentId) return
    activeDetailIdRef.current = contentId

    if (detailCache[contentId]) {
      setDestinationDetail(detailCache[contentId])
      setDestinationDetailError(null)
      setDestinationDetailLoading(false)
      return
    }

    setDestinationDetail(null)
    setDestinationDetailError(null)
    setDestinationDetailLoading(true)

    try {
      const detail = await fetchTouristSpotDetail(contentId)
      setDetailCache((prev) => ({ ...prev, [contentId]: detail }))
      if (activeDetailIdRef.current === contentId) {
        setDestinationDetail(detail)
        setDestinationDetailError(null)
      }
    } catch (error) {
      console.error('detail fetch error', error)
      if (activeDetailIdRef.current === contentId) {
        setDestinationDetailError(error.message || '상세 정보를 불러오는 중 문제가 발생했습니다.')
      }
    } finally {
      if (activeDetailIdRef.current === contentId) {
        setDestinationDetailLoading(false)
      }
    }
  }, [detailCache])

  const handleCardClick = async (card) => {
    const base = {
      ...card,
      tags: card.tags || [],
    }
    setSelectedDestination(base)
    const contentId = card.contentId || card.id
    await loadDestinationDetail(contentId)
  }

  const handleRetryDetail = useCallback(() => {
    const contentId = selectedDestination?.contentId || selectedDestination?.id
    if (!contentId) return
    loadDestinationDetail(contentId)
  }, [loadDestinationDetail, selectedDestination])

  const handleCloseDestination = useCallback(() => {
    setSelectedDestination(null)
    setDestinationDetail(null)
    setDestinationDetailError(null)
    setDestinationDetailLoading(false)
    activeDetailIdRef.current = null
  }, [])

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
                <p>{card.previewText}</p>
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
        // 백엔드 라우팅(/api/service/weather/current/)에 맞춰 엔드포인트 수정
        const w = await requestJson(`${API_BASE}/api/service/weather/current/`)
        const summary = formatWeatherSummary(w) || '날씨 정보를 가져오지 못했어요.'
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
            onClose={handleCloseDestination}
            isSaved={false}
            onToggleSave={() => console.log('찜하기 눌림')}
            detail={destinationDetail}
            detailLoading={destinationDetailLoading}
            detailError={destinationDetailError}
            onRetryDetail={handleRetryDetail}
          />
        )}
      </div>
    </div>
  )
}

export default ChatbotView
