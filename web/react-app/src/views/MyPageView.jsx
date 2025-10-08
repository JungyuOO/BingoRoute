import { useState } from 'react'
import './MyPageView.css'
import '../components/features/destinations/Destinations.css'
import DestinationCard from '../components/features/destinations/DestinationCard'
import TripDetailModal from '../components/features/trips/TripDetailModal'
import { useStore } from '../context/StoreContext'
import { DESTINATIONS } from '../data/destinations'

const MyPageView = () => {
  const { session, setSession, wishlist, trips, removeDestinationFromTrip, deleteTrip, mergeTrips, updateTrip } = useStore()
  const [isEditing, setIsEditing] = useState(false)
  const [isTripModalOpen, setIsTripModalOpen] = useState(false)
  const [selectedTrip, setSelectedTrip] = useState(null)
  const [editingTripId, setEditingTripId] = useState(null)
  const [mergeTarget, setMergeTarget] = useState('')
  const [mergeSource, setMergeSource] = useState('')
  const [editForm, setEditForm] = useState({
    name: session?.name || session?.first_name || '',
    email: session?.email || ''
  })

  const handleEditStart = () => {
    setEditForm({
      name: session?.name || session?.first_name || '',
      email: session?.email || ''
    })
    setIsEditing(true)
  }

  const handleEditCancel = () => {
    setIsEditing(false)
    setEditForm({
      name: session?.name || session?.first_name || '',
      email: session?.email || ''
    })
  }

  const handleEditSave = () => {
    const updatedSession = {
      ...session,
      name: editForm.name,
      first_name: editForm.name,
      email: editForm.email
    }
    setSession(updatedSession)
    setIsEditing(false)
    alert('회원정보가 수정되었습니다!')
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setEditForm(prev => ({
      ...prev,
      [name]: value
    }))
  }

  if (!session) {
    return (
      <div className="br-container">
        <div className="center">
          <p>로그인이 필요합니다.</p>
        </div>
      </div>
    )
  }

  const wishlistDestinations = DESTINATIONS.filter(d => wishlist.includes(d.id))

  const getWeatherScoreClass = (score) => {
    if (score >= 80) return 'excellent'
    if (score >= 70) return 'good'
    if (score >= 60) return 'fair'
    if (score >= 50) return 'average'
    return 'poor'
  }

  const getWeatherIcon = (score) => {
    if (score >= 80) return '☀️'
    if (score >= 70) return '🌤️'
    if (score >= 60) return '⛅️'
    if (score >= 50) return '☁️'
    return '🌧️'
  }

  const getWeatherMessage = (score) => {
    if (score >= 80) return '완벽한 여행 날씨!'
    if (score >= 70) return '여행하기 좋은 날씨'
    if (score >= 60) return '괜찮은 날씨'
    if (score >= 50) return '보통 날씨'
    return '주의가 필요한 날씨'
  }

  const formatDateRange = (trip) => {
    const { startDate, endDate } = trip || {}
    if (!startDate && !endDate) return '날짜 미정'
    if (startDate && !endDate) return startDate
    if (!startDate && endDate) return endDate
    return `${startDate} ~ ${endDate}`
  }

  const getTripStatus = (trip) => {
    const today = new Date().toISOString().slice(0,10)
    const start = trip?.startDate || null
    const end = trip?.endDate || null
    if (!start && !end) return null
    // Only start
    if (start && !end) {
      if (today < start) return '예정'
      if (today === start) return '여행중'
      return '완료'
    }
    // Only end
    if (!start && end) {
      if (today < end) return '예정'
      if (today === end) return '여행중'
      return '완료'
    }
    // Both start and end
    if (today < start) return '예정'
    if (today > end) return '완료'
    return '여행중'
  }

  const shareTrip = async (trip) => {
    const names = (trip.destinations || trip.routes || []).map(d => {
      const m = DESTINATIONS.find(x => x.id === d || x.name === d)
      return m?.name || d
    })
    const text = `여행 계획: ${trip.title}\n기간: ${formatDateRange(trip)}\n경로: ${names.join(' > ')}`
    const url = `${window.location.origin}/mypage?trip=${encodeURIComponent(trip.id)}`
    try {
      if (navigator.share) {
        await navigator.share({ title: trip.title, text, url })
      } else {
        await navigator.clipboard.writeText(`${text}\n${url}`)
        alert('공유 링크가 클립보드에 복사되었습니다!')
      }
    } catch (e) {
      console.error(e)
      alert('공유 중 오류가 발생했어요.')
    }
  }

  const openTripModal = (trip) => {
    setSelectedTrip(trip)
    setIsTripModalOpen(true)
  }

  const closeTripModal = () => {
    setIsTripModalOpen(false)
    setSelectedTrip(null)
  }

  return (
    <div className="br-container">
      <div className="section">
        <div className="section-header">
          <h2>회원 정보</h2>
          {!isEditing ? (
            <button className="btn-edit" onClick={handleEditStart}>
              회원정보 수정하기
            </button>
          ) : (
            <div className="edit-actions">
              <button className="btn-save" onClick={handleEditSave}>
                저장
              </button>
              <button className="btn-cancel" onClick={handleEditCancel}>
                취소
              </button>
            </div>
          )}
        </div>

        <div className="panel">
          {!isEditing ? (
            <div className="grid-2">
              <div>
                <strong>이름</strong>
                <p>{session.name || session.first_name || ''}</p>
              </div>
              <div>
                <strong>이메일</strong>
                <p>{session.email}</p>
              </div>
            </div>
          ) : (
            <div className="edit-form">
              <div className="form-group">
                <label htmlFor="name">
                  <strong>이름</strong>
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={editForm.name}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="이름을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">
                  <strong>이메일</strong>
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={editForm.email}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="이메일을 입력하세요"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="section">
        <h3>찜한 장소 ({wishlist.length})</h3>
        {wishlistDestinations.length > 0 ? (
          <div className="cards">
            {wishlistDestinations.map(destination => (
              <DestinationCard key={destination.id} destination={destination} />
            ))}
          </div>
        ) : (
          <div className="center">
            <p className="muted">찜한 장소가 없습니다.</p>
          </div>
        )}
      </div>

      <div className="section">
        <h3>나의 여행 계획 ({trips.length})</h3>
        {trips.length > 1 && (
          <div className="merge-row" style={{display:'flex',gap:8,alignItems:'center',margin:'8px 0 16px'}}>
            <span className="muted" style={{minWidth:72}}>계획 병합</span>
            <select className="form-input" value={mergeTarget} onChange={(e)=>setMergeTarget(e.target.value)} style={{maxWidth:220}}>
              <option value="">대상 선택</option>
              {trips.map(t => <option key={t.id} value={t.id}>{t.title || '여행 계획'}</option>)}
            </select>
            <span>⬅︎</span>
            <select className="form-input" value={mergeSource} onChange={(e)=>setMergeSource(e.target.value)} style={{maxWidth:220}}>
              <option value="">합칠 계획</option>
              {trips.map(t => <option key={t.id} value={t.id}>{t.title || '여행 계획'}</option>)}
            </select>
            <button className="btn-save" onClick={()=>{
              if (!mergeTarget || !mergeSource || mergeTarget===mergeSource) return alert('서로 다른 두 계획을 선택하세요.')
              mergeTrips(mergeTarget, [mergeSource])
              setMergeTarget('')
              setMergeSource('')
              alert('계획을 병합했습니다.')
            }}>병합</button>
          </div>
        )}
        {trips.length > 0 ? (
          <div className="trip-list">
            {trips.map((trip, index) => (
              <div
                key={index}
                className="trip-button"
                style={{position:'relative'}}
                role="button"
                tabIndex={0}
                onClick={() => openTripModal(trip)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openTripModal(trip) } }}
              >
                <div className="trip-button-header">
                  <div>
                    <div className="trip-button-title">{trip.title || `여행 계획 ${index + 1}`}</div>
                    <div className="trip-button-meta">
                      <span>{formatDateRange(trip)}</span>
                    </div>
                  </div>
                  <div style={{display:'flex',gap:8, alignItems:'center'}}>
                    {(() => {
                      const status = getTripStatus(trip)
                      if (!status) return null
                      const cls = status === '예정' ? 'planned' : status === '여행중' ? 'ongoing' : 'done'
                      return <span className={`status-badge ${cls}`}>{status}</span>
                    })()}
                  </div>
                </div>
                <div className="trip-button-content">
                  <div className="trip-destinations">
                    {(trip.destinations || trip.routes || []).length > 0 ? (
                      (trip.destinations || trip.routes).map((d, i) => {
                        const dest = DESTINATIONS.find(x => x.id === d || x.name === d)
                        return (
                          <span key={`${d}-${i}`} className="destination-tag" style={{display:'inline-flex',alignItems:'center',gap:6}}>
                            {dest?.name || d}
                            {editingTripId===trip.id && (
                              <button className="btn-cancel" onClick={(e)=> { e.stopPropagation(); removeDestinationFromTrip(trip.id, d) }} style={{padding:'0 6px'}}>×</button>
                            )}
                          </span>
                        )
                      })
                    ) : (
                      <span className="weather-message-small">경로 없음</span>
                    )}
                  </div>
                  <div className="trip-actions-row">
                    <button className="btn-edit" onClick={(e)=> { e.stopPropagation(); setEditingTripId(editingTripId===trip.id ? null : trip.id) }}>{editingTripId===trip.id ? '수정 완료' : '수정하기'}</button>
                    <button className="btn-share" onClick={(e)=> { e.stopPropagation(); shareTrip(trip) }}>공유하기</button>
                  </div>
                  {editingTripId===trip.id && (
                    <div style={{display:'flex',gap:8,marginTop:8}}>
                      <button className="btn-cancel" onClick={(e)=> { e.stopPropagation(); deleteTrip(trip.id) }}>여행 삭제</button>
                    </div>
                  )}
                  {editingTripId===trip.id && (
                    <div className="dates-row">
                      <label>시작일<input type="date" value={trip.startDate || ''} onClick={(e)=> e.stopPropagation()} onChange={(e)=> updateTrip(trip.id, { startDate: e.target.value })} /></label>
                      <label>종료일<input type="date" value={trip.endDate || ''} onClick={(e)=> e.stopPropagation()} onChange={(e)=> updateTrip(trip.id, { endDate: e.target.value })} /></label>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="center">
            <p className="muted">저장된 여행 계획이 없습니다.</p>
            <p className="muted">AI와 함께 새로운 여행을 계획해보세요!</p>
          </div>
        )}
      </div>

      <TripDetailModal trip={selectedTrip} isOpen={isTripModalOpen} onClose={closeTripModal} />
    </div>
  )
}

export default MyPageView
