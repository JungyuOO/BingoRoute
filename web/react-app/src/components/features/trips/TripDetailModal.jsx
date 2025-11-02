import { useEffect, useMemo, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '../../ui'
// 더미데이터 제거 - 실제 API 사용
import './TripDetailModal.css'
import '../destinations/DestinationDetailModal.css'

const TripDetailModal = ({ trip, isOpen, onClose }) => {
  const [destinations, setDestinations] = useState([])
  const [loadingDestinations, setLoadingDestinations] = useState(false)
  const [index, setIndex] = useState(0)

  // 실제 API에서 관광지 데이터 가져오기
  useEffect(() => {
    if (!isOpen || !trip) return

    const fetchDestinations = async () => {
      try {
        setLoadingDestinations(true)
        const response = await fetch('http://localhost:8000/api/service/tourist_spots/')
        const data = await response.json()

        if (response.ok && Array.isArray(data.results)) {
          // tourist_spot 테이블 데이터 사용
          const transformedData = data.results.map(item => ({
            id: item.content_id,
            name: item.title,
            area: item.area_name || item.category_name || '관광지', // tourist_spot_detail에서 가져온 지역 정보
            rating: null, // tourist_spot 테이블에는 평점 정보 없음
            duration: '2-3시간', // 기본값
            tags: item.category_name ? [item.category_name] : ['관광지'],
            short: item.title,
            long: item.title,
            image: item.firstimage || item.firstimage2,
            phone: null,
            closedDays: null,
            operatingHours: null,
            operatingSeason: null,
            parking: null,
            strollerFriendly: null,
            petFriendly: null,
            creditCard: null
          }))
          setDestinations(transformedData)
        }
      } catch (error) {
        console.error('⚠️ 관광지 API 요청 오류:', error)
        setDestinations([])
      } finally {
        setLoadingDestinations(false)
      }
    }

    fetchDestinations()
  }, [isOpen, trip])

  const steps = useMemo(() => {
    const ids = trip?.destinations || trip?.routes || []
    // map id or name to destination object
    return ids
      .map((idOrName) => destinations.find(d => d.id === idOrName || d.name === idOrName))
      .filter(Boolean)
  }, [trip, destinations])

  useEffect(() => {
    if (!isOpen) return
    setIndex(0)
  }, [isOpen, trip])

  useEffect(() => {
    if (!isOpen) return
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowRight') next()
      if (e.key === 'ArrowLeft') prev()
    }
    document.addEventListener('keydown', onKey)
    const { overflow } = document.body.style
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = overflow
    }
  }, [isOpen])

  const prev = useCallback(() => setIndex(i => (i > 0 ? i - 1 : i)), [])
  const next = useCallback(() => setIndex(i => (i < steps.length - 1 ? i + 1 : i)), [steps.length])

  if (!isOpen || typeof document === 'undefined') return null

  const current = steps[index]

  return createPortal(
    <div className="destination-modal__backdrop" onClick={onClose}>
      <div className="destination-modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="destination-modal__header">
          <div>
            <h2>{trip?.title || '내 여행 계획'}</h2>
            <ul className="destination-modal__tags" style={{marginTop:8}}>
              {(trip?.destinations || trip?.routes || []).map((t, i) => (
                <li key={`${t}-${i}`}>{destinations.find(d => d.id === t || d.name === t)?.name || t}</li>
              ))}
            </ul>
          </div>
          <button type="button" className="destination-modal__close" onClick={onClose} aria-label="닫기">×</button>
        </div>

        {loadingDestinations ? (
          <div className="destination-modal__content">관광지 정보를 불러오는 중...</div>
        ) : steps.length === 0 ? (
          <div className="destination-modal__content">경로가 비어있습니다.</div>
        ) : (
          <div className="destination-modal__content" style={{position:'relative',display:'grid',gridTemplateColumns:'40px 1fr 40px',gap:8}}>
            <button type="button" className="nav-btn left" onClick={prev} disabled={index === 0} aria-label="이전">‹</button>

            <div>
              {/* 모달창 맨 상단 여행지명 부분 */}
              <div className="modal-hero">
                <div className="modal-hero__tags">
                  <span className="modal-tag">{index + 1} / {steps.length}</span>
                  {current?.tags?.map(tag => (
                    <span key={tag} className="modal-tag">{tag}</span>
                  ))}
                </div>
                <h2 className="modal-hero__title">{current?.name}</h2>
                <p className="modal-hero__meta">📍{current?.area} · ⭐ {current?.rating}</p>
              </div>

              {/* 상세정보 부분 */}
              <div className="modal-section">
                <h3>상세 정보</h3>
                <p>{current?.long || current?.short}</p>
              </div>

              {/* 모달창 방문정보 부분*/}
              <div className="modal-section">
                <h3>방문 정보</h3>
                <div className="modal-info-grid">
                  <div>
                    <strong>전화번호</strong>
                    <p>{current?.phone || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>휴무일</strong>
                    <p>{current?.closedDays || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>운영시간</strong>
                    <p>{current?.operatingHours || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>운영계절</strong>
                    <p>{current?.operatingSeason || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>주차장</strong>
                    <p>{current?.parking ? '이용 가능' : '이용 불가'}</p>
                  </div>
                  <div>
                    <strong>유모차</strong>
                    <p>{current?.strollerFriendly ? '이용 가능' : '이용 불가'}</p>
                  </div>
                  <div>
                    <strong>반려동물 입장</strong>
                    <p>{current?.petFriendly ? '입장 가능' : '입장 불가'}</p>
                  </div>
                  <div>
                    <strong>신용카드</strong>
                    <p>{current?.creditCard ? '사용 가능' : '사용 불가'}</p>
                  </div>
                </div>
              </div>
            </div>

            <button type="button" className="nav-btn right" onClick={next} disabled={index === steps.length - 1} aria-label="다음">›</button>
          </div>
        )}

        <div className="destination-modal__actions">
          <Button variant="ghost" onClick={onClose} type="button">닫기</Button>
        </div>
      </div>
    </div>,
    document.body
  )
}

export default TripDetailModal
