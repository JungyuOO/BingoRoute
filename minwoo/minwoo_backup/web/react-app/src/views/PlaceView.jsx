import { useParams, useNavigate } from 'react-router-dom'
import { DESTINATIONS } from '../data/destinations'
import { useStore } from '../context/StoreContext'
import { useAuth } from '../hooks/useAuth'

const PlaceView = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { wishlist, setWishlist } = useStore()
  const { isAuthenticated, promptLogin } = useAuth()
  
  const destination = DESTINATIONS.find(d => d.id === id)
  
  if (!destination) {
    return (
      <div className="br-container">
        <div className="center">
          <p>장소를 찾을 수 없습니다.</p>
          <button className="brand-btn" onClick={() => navigate('/')}>
            홈으로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  const isSaved = wishlist.includes(destination.id)

  const toggleSave = () => {
    if (!isAuthenticated) return
    const newWishlist = isSaved 
      ? wishlist.filter(id => id !== destination.id)
      : [...wishlist, destination.id]
    setWishlist(newWishlist)
  }

  return (
    <div className="br-container">
      <div className="section">
        <button className="ghost-btn" onClick={() => navigate(-1)}>
          ← 뒤로가기
        </button>
      </div>

      <div className="section">
        <div className="hero" style={{ background: '#c7d2fe' }}>
          <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div className="pill" style={{ marginBottom: '8px' }}>
                {destination.tags.join(' · ')}
              </div>
              <h1>{destination.name}</h1>
              <p>{destination.area} · 평점 {destination.rating} · {destination.duration}</p>
            </div>
            <button 
              className="ghost-btn" 
              onClick={toggleSave} 
              style={{ background: 'rgba(255,255,255,0.2)' }}
              disabled={!isAuthenticated}
              title={!isAuthenticated ? '로그인 후 이용해주세요' : ''}
            >
              {isSaved ? '찜 해제' : '찜하기'}
            </button>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="panel">
          <h3>상세 정보</h3>
          <p>{destination.long}</p>
        </div>
      </div>

      <div className="section">
        <div className="panel">
          <h3>방문 정보</h3>
          <div className="grid-2">
            <div>
              <strong>추천 소요시간</strong>
              <p>{destination.duration}</p>
            </div>
            <div>
              <strong>평점</strong>
              <p>{destination.rating}/5.0</p>
            </div>
          </div>
          <div>
            <strong>태그</strong>
            <div style={{ marginTop: '8px' }}>
              {destination.tags.map(tag => (
                <span key={tag} className="pill" style={{ marginRight: '8px' }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="section">
        <button
          className="brand-btn"
          style={{ width: '100%' }}
          onClick={() => {
            if (!isAuthenticated) return promptLogin()
            navigate('/planner')
          }}
        >
          여행 계획에 추가하기
        </button>
      </div>
    </div>
  )
}

export default PlaceView
