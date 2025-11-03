import { useNavigate } from 'react-router-dom'

const ChatHeader = () => {
  const navigate = useNavigate()
  return (
    <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
      <div className="row" style={{ gap: 20 }}>
        <button className="ghost-btn" onClick={() => navigate(-1)}> 🏠︎ 홈으로</button>
        <div className="row" style={{ gap: 10 }}>
          <div className="badge" style={{ background: '#FC7B54' }}>★</div>
          <strong>AI 여행 플래너</strong>
        </div>
      </div>
      <span className="pill" style={{ background: '#ecfdf5', borderColor: '#bbf7d0', color: '#166534' }}>온라인</span>
    </div>
  )
}

export default ChatHeader

