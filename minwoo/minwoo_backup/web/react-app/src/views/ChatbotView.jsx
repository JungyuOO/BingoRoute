import { useEffect, useState } from 'react'
import ChatHeader from '../components/chat/ChatHeader'
import ChatMessage from '../components/chat/ChatMessage'
import QuickReplies from '../components/chat/QuickReplies'
import ChatInput from '../components/chat/ChatInput'

const INITIAL_CHIPS = [
  '역사와 문화 탐방',
  '쇼핑과 맛집 투어',
  '자연과 힐링',
  '핫플레이스 탐방',
  '전통 체험'
]

const systemGreeting = (
  <>
    <p style={{ margin: 0 }}>안녕하세요! 빙고루트 AI 여행 플래너입니다. ✨</p>
    <p style={{ margin: '6px 0 0 0' }}>서울에서의 완벽한 여행 계획을 함께 세워보아요!</p>
    <p style={{ margin: '6px 0 0 0' }}>어떤 스타일의 여행을 원하시나요?</p>
  </>
)

const mockReply = (text) => {
  // 간단한 규칙 기반 모의 응답
  if (text.includes('역사') || text.includes('문화')) {
    return '경복궁, 북촌 한옥마을, 서촌 일대를 중심으로 2~3시간 코스를 추천해요. 한복 대여와 함께 사진 스팟도 안내해드릴게요.'
  }
  if (text.includes('쇼핑') || text.includes('맛집')) {
    return '명동-남대문-회현동 라인을 따라 쇼핑과 맛집을 함께 즐겨보세요. 비 오는 날에도 즐기기 좋아요.'
  }
  if (text.includes('자연') || text.includes('힐링')) {
    return '서울숲-뚝섬 한강공원 코스로 여유로운 산책을 추천합니다. 카페와 피크닉 스팟도 함께 알려드릴게요.'
  }
  if (text.includes('핫플') || text.includes('핫플레이스')) {
    return '성수-연남-한남 핫플 투어로 요즘 트렌디한 공간들을 둘러보는 코스를 짜드릴게요.'
  }
  if (text.includes('전통')) {
    return '인사동-익선동-낙원상가를 잇는 전통 체험 루트를 추천합니다. 공예 체험과 전통 다과 코스도 가능해요.'
  }
  return '좋아요! 선호하시는 기간과 동행, 예산을 알려주시면 더 맞춤형 코스를 제안할게요.'
}

const ChatbotView = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', content: systemGreeting }
  ])
  const [chips, setChips] = useState(INITIAL_CHIPS)

  const pushMessage = (role, content) => {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), role, content }])
  }

  const handleSend = (text) => {
    pushMessage('user', <span>{text}</span>)
    // 간단한 지연 후 응답 추가 (실서비스는 API 연동)
    const reply = mockReply(text)
    setTimeout(() => pushMessage('assistant', <span>{reply}</span>), 300)
  }

  const handleChip = (label) => {
    handleSend(label)
    // 칩은 최근 선택 기반으로 일부 유지
    setChips((prev) => [label, ...INITIAL_CHIPS.filter((c) => c !== label)].slice(0, 5))
  }

  useEffect(() => {
    document.title = 'AI 여행 플래너'
  }, [])

  return (
    <div className="br-container">
      <ChatHeader />

      <div className="section">
        {/* 대화 영역 */}
        <div style={{ minHeight: '46vh' }}>
          {messages.map((m) => (
            <ChatMessage key={m.id} role={m.role}>{m.content}</ChatMessage>
          ))}
        </div>

        {/* 빠른 선택 칩 */}
        <div style={{ margin: '8px 0 16px' }}>
          <QuickReplies options={chips} onSelect={handleChip} />
        </div>

        {/* 입력 영역 */}
        <ChatInput onSend={handleSend} />

        <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>
          AI가 생성한 답변입니다. 실제 정보와 다를 수 있으니 참고용으로만 활용해주세요.
        </div>
      </div>
    </div>
  )
}

export default ChatbotView

