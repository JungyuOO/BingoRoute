import { useEffect, useMemo, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '../../ui'
// 더미데이터 제거 - 실제 API 사용
import './TripDetailModal.css'
import '../destinations/DestinationDetailModal.css'

const TripDetailModal = ({ trip, isOpen, onClose }) => {
  const [destinations, setDestinations] = useState([])
  const [loadingDestinations, setLoadingDestinations] = useState(false)
  const [destinationDetails, setDestinationDetails] = useState({})
  const [loadingDetails, setLoadingDetails] = useState({})
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
            area: item.area_name || item.category_name || '관광지',
            rating: null,
            duration: '2-3시간',
            tags: item.category_name ? [item.category_name] : ['관광지'],
            short: item.title,
            long: item.title,
            image: item.firstimage || item.firstimage2
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

  // 🔹 각 여행지의 상세 정보 가져오기 (DestinationDetailModal과 동일한 로직)
  const fetchDestinationDetails = async (destinationId) => {
    if (destinationDetails[destinationId] || loadingDetails[destinationId]) return

    try {
      setLoadingDetails(prev => ({ ...prev, [destinationId]: true }))
      console.log('🔄 관광지 상세정보 요청:', destinationId)
      const response = await fetch(`http://localhost:8000/api/service/tourist_spots/detail/${destinationId}/`)
      const data = await response.json()
      console.log('📊 상세정보 API 응답:', { status: response.status, data })

      if (response.ok && data.results && Array.isArray(data.results)) {
        const details = {}

        data.results.forEach(item => {
          if (item.tel) details.phone = item.tel
          if (item.restdate) details.closedDays = item.restdate
          if (item.usetime) details.operatingHours = item.usetime
          if (item.useseason) details.operatingSeason = item.useseason
          if (item.address) details.address = item.address

          if (item.is_parking) details.parking = item.is_parking === '1' || item.is_parking === 1
          if (item.is_baby_carriage) details.strollerFriendly = item.is_baby_carriage === '1' || item.is_baby_carriage === 1
          if (item.is_pet) details.petFriendly = item.is_pet === '1' || item.is_pet === 1
          if (item.is_credit_card) details.creditCard = item.is_credit_card === '1' || item.is_credit_card === 1

          if (item.info_text) {
            if (!details.descriptions) details.descriptions = []
            details.descriptions.push({
              name: item.info_name || '정보',
              text: item.info_text
            })
          }
        })

        setDestinationDetails(prev => ({ ...prev, [destinationId]: details }))
        console.log('✅ 상세정보 로드 완료:', details)
      }
    } catch (error) {
      console.error('⚠️ 관광지 상세정보 API 요청 오류:', error)
    } finally {
      setLoadingDetails(prev => ({ ...prev, [destinationId]: false }))
    }
  }

  const steps = useMemo(() => {
    const ids = trip?.destinations || trip?.routes || []
    // map id or name to destination object
    return ids
      .map((idOrName) => destinations.find(d => d.id === idOrName || d.name === idOrName))
      .filter(Boolean)
  }, [trip, destinations])

  // 현재 표시 중인 여행지의 상세 정보 가져오기
  useEffect(() => {
    if (!isOpen || steps.length === 0) return
    const currentDestination = steps[index]
    if (currentDestination?.id) {
      fetchDestinationDetails(currentDestination.id)
    }
  }, [isOpen, index, steps])

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
  const currentDetails = current?.id ? destinationDetails[current.id] : null
  const isLoadingCurrentDetails = current?.id ? loadingDetails[current.id] : false

  return createPortal(
    <div className="destination-modal__backdrop" onClick={onClose}>
      <div className="destination-modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="destination-modal__header">
          <div>
            <h2>{trip?.title || '내 여행 계획'}</h2>
            <ul className="destination-modal__tags" style={{ marginTop: 8 }}>
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
          <div className="destination-modal__content" style={{ position: 'relative', display: 'grid', gridTemplateColumns: '40px 1fr 40px', gap: 8 }}>
            <button type="button" className="nav-btn left" onClick={prev} disabled={index === 0} aria-label="이전">‹</button>

            <div>
              {/* 모달창 맨 상단 여행지명 부분 */}
              <div className="modal-hero">
                {current?.image && (
                  <div className="modal-hero__image">
                    <img
                      src={current.image}
                      alt={current.name}
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  </div>
                )}
                <div className="modal-hero__tags">
                  <span className="modal-tag">{index + 1} / {steps.length}</span>
                  {current?.tags?.map(tag => (
                    <span key={tag} className="modal-tag">{tag}</span>
                  ))}
                </div>
                <h2 className="modal-hero__title">{current?.name}</h2>
                <p className="modal-hero__meta">
                  📍{currentDetails?.area || current?.area}
                  {current?.rating && ` · ⭐ ${current?.rating}`}
                </p>
              </div>

              {/* 상세정보 부분 */}
              <div className="modal-section">
                <h3>상세 정보</h3>
                {isLoadingCurrentDetails ? (
                  <p>상세 정보를 불러오는 중...</p>
                ) : (
                  <>
                    {currentDetails?.descriptions && currentDetails.descriptions.length > 0 ? (
                      currentDetails.descriptions.map((desc, descIndex) => (
                        <div key={descIndex} style={{ marginBottom: '1rem' }}>
                          <h4 style={{ fontSize: '0.9rem', color: '#5EABA2', marginBottom: '0.5rem' }}>
                            {desc.name}
                          </h4>
                          <p>{desc.text}</p>
                        </div>
                      ))
                    ) : (
                      <p>{current?.long || current?.short}</p>
                    )}
                    {currentDetails?.address && (
                      <p><strong>주소:</strong> {currentDetails.address}</p>
                    )}
                  </>
                )}
              </div>

              {/* 모달창 방문정보 부분*/}
              <div className="modal-section">
                <h3>방문 정보</h3>
                {isLoadingCurrentDetails ? (
                  <p>방문 정보를 불러오는 중...</p>
                ) : (
                  <div className="modal-info-grid">
                    <div>
                      <strong>전화번호</strong>
                      <p>{currentDetails?.phone || '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>휴무일</strong>
                      <p>{currentDetails?.closedDays || '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>운영시간</strong>
                      <p>{currentDetails?.operatingHours || '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>운영계절</strong>
                      <p>{currentDetails?.operatingSeason || '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>주차장</strong>
                      <p>{currentDetails?.parking !== undefined ? (currentDetails.parking ? '이용 가능' : '이용 불가') : '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>유모차</strong>
                      <p>{currentDetails?.strollerFriendly !== undefined ? (currentDetails.strollerFriendly ? '이용 가능' : '이용 불가') : '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>반려동물 입장</strong>
                      <p>{currentDetails?.petFriendly !== undefined ? (currentDetails.petFriendly ? '입장 가능' : '입장 불가') : '정보 없음'}</p>
                    </div>
                    <div>
                      <strong>신용카드</strong>
                      <p>{currentDetails?.creditCard !== undefined ? (currentDetails.creditCard ? '사용 가능' : '사용 불가') : '정보 없음'}</p>
                    </div>
                  </div>
                )}
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