import { useState } from 'react'
import './MyPageView.css'
import '../components/features/destinations/Destinations.css'
import DestinationCard from '../components/features/destinations/DestinationCard'
import TripDetailModal from '../components/features/trips/TripDetailModal'
import { useStore } from '../context/StoreContext'
import { DESTINATIONS } from '../data/destinations'

const MyPageView = () => {
  const { session, setSession, wishlist, trips, removeDestinationFromTrip, deleteTrip, mergeTrips, updateTrip, replanTrip } = useStore()
  const [isEditing, setIsEditing] = useState(false)
  const [isTripModalOpen, setIsTripModalOpen] = useState(false)
  const [selectedTrip, setSelectedTrip] = useState(null)
  const [editingTripId, setEditingTripId] = useState(null)
  const [mergeTarget, setMergeTarget] = useState('')
  const [mergeSource, setMergeSource] = useState('')
  const [editForm, setEditForm] = useState({
    password: '',
    confirmPassword: ''
  })

  const handleEditStart = () => {
    setEditForm({
      password: '',
      confirmPassword: ''
    })
    setIsEditing(true)
  }

  const handleEditCancel = () => {
    setIsEditing(false)
    setEditForm({
      password: '',
      confirmPassword: ''
    })
  }

  const handleEditSave = () => {
    // 비밀번호 입력 확인
    if (!editForm.password.trim()) {
      alert('새 비밀번호를 입력해주세요.')
      return
    }

    // 비밀번호 확인 검증
    if (editForm.password !== editForm.confirmPassword) {
      alert('비밀번호가 일치하지 않습니다.')
      return
    }

    // 비밀번호 길이 검증
    if (editForm.password.length < 6) {
      alert('비밀번호는 최소 6자 이상이어야 합니다.')
      return
    }

    const updatedSession = {
      ...session,
      password: editForm.password
    }

    setSession(updatedSession)
    setIsEditing(false)
    alert('비밀번호가 변경되었습니다!')
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



  const formatDateRange = (trip) => {
    const { startDate, endDate } = trip || {}
    if (!startDate && !endDate) return '날짜 미정'
    if (startDate && !endDate) return startDate
    if (!startDate && endDate) return endDate
    return `${startDate} ~ ${endDate}`
  }


  // 여행 상태표시
  const getTripStatus = (trip) => {
    const today = new Date().toISOString().slice(0, 10)
    const start = trip?.startDate || null
    const end = trip?.endDate || null
    if (!start && !end) return null
    if (start && !end) {
      if (today < start) return '예정'
      if (today === start) return '여행중'
      return '완료'
    }
    if (!start && end) {
      if (today < end) return '예정'
      if (today === end) return '여행중'
      return '완료'
    }
    if (today < start) return '예정'
    if (today > end) return '완료'
    return '여행중'
  }


  // 여행계획 공유하기 -> 해당 여행계획의 url이 복사됨.
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

  // 모달창 
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
              비밀번호 변경
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
                <strong>사용자 ID</strong>
                <p>{session.user_id || session.userId || session.username || '미입력'}</p>
              </div>
              <div>
                <strong>이름</strong>
                <p>{session.name || session.first_name || '미입력'}</p>
              </div>
              <div>
                <strong>이메일</strong>
                <p>{session.email || '미입력'}</p>
              </div>
              <div>
                <strong>생년월일</strong>
                <p>{session.birth_date || session.birthDate || '미입력'}</p>
              </div>
              <div>
                <strong>성별</strong>
                <p>{
                  session.gender === 'M' ? '남성' : 
                  session.gender === 'F' ? '여성' : 
                  session.gender === 'O' ? '기타' :
                  session.gender === 'male' ? '남성' : 
                  session.gender === 'female' ? '여성' : 
                  session.gender || '미입력'
                }</p>
              </div>
            </div>
          ) : (
            <div className="edit-form">
              <div className="readonly-info">
                <div className="grid-2">
                  <div>
                    <strong>사용자 ID</strong>
                    <p>{session.user_id || session.userId || session.username || '미입력'}</p>
                  </div>
                  <div>
                    <strong>이름</strong>
                    <p>{session.name || session.first_name || '미입력'}</p>
                  </div>
                  <div>
                    <strong>이메일</strong>
                    <p>{session.email || '미입력'}</p>
                  </div>
                  <div>
                    <strong>생년월일</strong>
                    <p>{session.birth_date || session.birthDate || '미입력'}</p>
                  </div>
                  <div>
                    <strong>성별</strong>
                    <p>{
                      session.gender === 'M' ? '남성' : 
                      session.gender === 'F' ? '여성' : 
                      session.gender === 'O' ? '기타' :
                      session.gender === 'male' ? '남성' : 
                      session.gender === 'female' ? '여성' : 
                      session.gender || '미입력'
                    }</p>
                  </div>
                </div>
              </div>
              <div className="password-change-section">
                <h4>비밀번호 변경</h4>
                <div className="form-group">
                  <label htmlFor="password">
                    <strong>새 비밀번호 *</strong>
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={editForm.password}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="새 비밀번호를 입력하세요 (최소 6자)"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="confirmPassword">
                    <strong>비밀번호 확인 *</strong>
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={editForm.confirmPassword}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="비밀번호를 다시 입력하세요"
                    required
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>


      {/* 마이페이지 찜한 장소 부분 */}

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


      {/* 마이페이지 나의 여행계획 부분 */}

      <div className="section">
        <h3>나의 여행 계획 ({trips.length})</h3>
        {trips.length > 1 && (
          <div className="merge-row" style={{ display: 'flex', gap: 8, alignItems: 'center', margin: '8px 0 16px' }}>
            <span className="muted" style={{ minWidth: 72 }}>계획 병합</span>
            <select className="form-input" value={mergeTarget} onChange={(e) => setMergeTarget(e.target.value)} style={{ maxWidth: 220 }}>
              <option value="">대상 선택</option>
              {trips.map(t => <option key={t.id} value={t.id}>{t.title || '여행 계획'}</option>)}
            </select>
            <span>⬅︎</span>
            <select className="form-input" value={mergeSource} onChange={(e) => setMergeSource(e.target.value)} style={{ maxWidth: 220 }}>
              <option value="">합칠 계획</option>
              {trips.map(t => <option key={t.id} value={t.id}>{t.title || '여행 계획'}</option>)}
            </select>
            <button className="btn-save" onClick={() => {
              if (!mergeTarget || !mergeSource || mergeTarget === mergeSource) return alert('서로 다른 두 계획을 선택하세요.')
              mergeTrips(mergeTarget, [mergeSource])
              setMergeTarget('')
              setMergeSource('')
              alert('계획을 병합했습니다.')
            }}>병합</button>
          </div>
        )}




export default MyPageView