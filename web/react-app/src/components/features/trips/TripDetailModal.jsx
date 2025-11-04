import { useEffect, useMemo, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '../../ui'
import './TripDetailModal.css'
import '../destinations/DestinationDetailModal.css'

import { DESTINATIONS } from '../../../data/destinations'
import { fetchTouristSpotDetail } from '../../../services/touristService'

const TripDetailModal = ({ trip, isOpen, onClose, resolveDestination }) => {
  const findDestination = useCallback((idOrName) => {
    if (!idOrName) return null
    if (resolveDestination) {
      const resolved = resolveDestination(idOrName)
      if (resolved) return resolved
    }
    return DESTINATIONS.find(d => d.id === idOrName || d.name === idOrName) || null
  }, [resolveDestination])

  const steps = useMemo(() => {
    const itineraries = trip?.itineraries || []

    return itineraries
      .map((item) => {
        const resolved = findDestination(item.content_id)
        if (resolved) return resolved

        return {
          id: item.content_id,
          name: `관광지 ${item.content_id}`,
          area: '정보 없음',
          rating: '정보 없음',
          tags: [],
          short: '상세 정보가 준비되지 않았습니다.',
        }
      })
      .filter(Boolean)
  }, [trip, findDestination])

  const [index, setIndex] = useState(0)

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

  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState(null)
  const [detailReloadKey, setDetailReloadKey] = useState(0)

  const current = steps[index] || null
  const currentId = current?.id || current?.raw?.content_id || null
  const canRequestDetail = !!currentId && !Number.isNaN(Number(currentId))

  useEffect(() => {
    if (!isOpen) return

    if (!canRequestDetail) {
      setDetail(null)
      setDetailError(null)
      setDetailLoading(false)
      return
    }

    let cancelled = false

    setDetail(null)
    setDetailError(null)
    setDetailLoading(true)

    fetchTouristSpotDetail(currentId)
      .then((detailData) => {
        if (!cancelled) {
          setDetail(detailData)
        }
      })
      .catch((error) => {
        if (!cancelled) {
          console.error('여행 상세 정보를 불러오지 못했습니다:', error)
          setDetailError(error.message || '상세 정보를 불러오는 중 문제가 발생했습니다.')
        }
      })
      .finally(() => {
        if (!cancelled) {
          setDetailLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [isOpen, canRequestDetail, currentId, detailReloadKey])

  const handleRetryDetail = useCallback(() => {
    if (!canRequestDetail) return
    setDetailReloadKey((key) => key + 1)
  }, [canRequestDetail])

  if (!isOpen || typeof document === 'undefined') return null

  const destination = current
  const heroImage = destination?.raw?.firstimage || destination?.raw?.firstimage2 || destination?.image || null

  return createPortal(
    <div className="destination-modal__backdrop" onClick={onClose}>
      <div className="destination-modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="destination-modal__header">
          <div>
            <h2>{trip?.title || '내 여행 계획'}</h2>
            <ul className="destination-modal__tags" style={{marginTop:8}}>
              {(trip?.itineraries || []).map((itinerary, i) => {
                const id = itinerary.content_id
                return <li key={`${id}-${itinerary.seq}-${i}`}>{findDestination(id)?.name || id}</li>
              })}
            </ul>
          </div>
          <button type="button" className="destination-modal__close" onClick={onClose} aria-label="닫기">×</button>
        </div>

        {steps.length === 0 ? (
          <div className="destination-modal__content">경로가 비어있습니다.</div>
        ) : (
          <div className="destination-modal__content" style={{position:'relative',display:'grid',gridTemplateColumns:'40px 1fr 40px',gap:8}}>
            <button type="button" className="nav-btn left" onClick={prev} disabled={index === 0} aria-label="이전">‹</button>

            <div>
              {/* 모달창 맨 상단 여행지명 부분 */}
              {heroImage && (
                <div className="modal-hero-image">
                  <img
                    src={heroImage}
                    alt={destination?.name ? `${destination.name} 대표 이미지` : '관광지 이미지'}
                    className="modal-hero-image__img"
                    loading="lazy"
                  />
                </div>
              )}
              <div className="modal-hero">
                <div className="modal-hero__tags">
                  <span className="modal-tag">{index + 1} / {steps.length}</span>
                  {destination?.tags?.map(tag => (
                    <span key={tag} className="modal-tag">{tag}</span>
                  ))}
                </div>
                <h2 className="modal-hero__title">{destination?.name}</h2>
                <p className="modal-hero__meta">📍{destination?.area} · ⭐ {destination?.rating}</p>
              </div>

              {/* 상세정보 부분 : DestinationModal과 동일하게 적용*/}
              <div className="modal-section">
                <h3>상세 정보</h3>
                {detailLoading ? (
                  <p>상세 정보를 불러오는 중입니다...</p>
                ) : detailError ? (
                  <div>
                    <p style={{ color: 'red', marginBottom: '8px' }}>{detailError}</p>
                    {canRequestDetail && (
                      <Button variant="ghost" onClick={handleRetryDetail}>
                        다시 시도
                      </Button>
                    )}
                  </div>
                ) : (
                  <p>{detail?.description || destination?.long || destination?.short}</p>
                )}
              </div>

              {/* 모달창 방문정보 부분 : DestinationModal과 동일하게 적용*/}
              <div className="modal-section">
                <h3>방문 정보</h3>
                <div className="modal-info-grid">
                  <div>
                    <strong>주소</strong>
                    <p>{detail?.address || destination?.area || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>전화번호</strong>
                    <p>{detail?.tel || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>휴무일</strong>
                    <p>{detail?.restdate || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>운영시간</strong>
                    <p>{detail?.usetime || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>운영계절</strong>
                    <p>{detail?.useseason || '정보 없음'}</p>
                  </div>
                  <div>
                    <strong>주차장</strong>
                    <p>{detail?.facilities?.parking ? '이용 가능' : '이용 불가'}</p>
                  </div>
                  <div>
                    <strong>유모차</strong>
                    <p>{detail?.facilities?.babyCarriage ? '이용 가능' : '이용 불가'}</p>
                  </div>
                  <div>
                    <strong>반려동물 입장</strong>
                    <p>{detail?.facilities?.pet ? '입장 가능' : '입장 불가'}</p>
                  </div>
                  <div>
                    <strong>신용카드</strong>
                    <p>{detail?.facilities?.creditCard ? '사용 가능' : '사용 불가'}</p>
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
