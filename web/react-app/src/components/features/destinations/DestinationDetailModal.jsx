import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '../../ui'
import Select from '../../ui/Select'
import { useAuth } from '../../../hooks/api/useAuth'
import { useStore } from '../../../context/StoreContext'
import './DestinationDetailModal.css'

const DestinationDetailModal = ({
  destination,
  isOpen,
  onClose,
  onNavigate,
  isSaved,
  onToggleSave,
}) => {
  const { isAuthenticated, promptLogin } = useAuth()
  const { trips, createTripWithDestination, appendDestinationToTrip } = useStore()
  const [selectedTripId, setSelectedTripId] = useState('NEW')
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    const { overflow } = document.body.style
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = overflow
    }
  }, [isOpen, onClose])

  if (!isOpen || typeof document === 'undefined') {
    return null
  }

  const handleBackdropClick = () => {
    onClose()
  }

  const handleContentClick = (event) => {
    event.stopPropagation()
  }

  const handleToggleSave = () => {
    onToggleSave()
  }

  const handlePlannerAdd = () => {
    if (!isAuthenticated) return promptLogin()

    const destKey = destination?.id || destination?.name
    if (!destKey) return

    if (selectedTripId === 'NEW' || trips.length === 0) {
      createTripWithDestination(destKey, { title: destination?.name })
      onClose()
      alert('새 여행 계획에 추가되었습니다!')
      return
    }

    // append to selected
    appendDestinationToTrip(selectedTripId, destKey)
    onClose()
    alert('선택한 여행 계획에 추가했습니다!')
  }

  return createPortal(
    <div className="destination-modal__backdrop" onClick={handleBackdropClick}>
      <div className="destination-modal" role="dialog" aria-modal="true" onClick={handleContentClick}>
        <div className="destination-modal__header">
          <button type="button" className="destination-modal__close" onClick={onClose} aria-label="닫기">
            ×
          </button>
        </div>

        <div className="destination-modal__content">
          {/* Hero Section */}
          <div className="modal-hero">
            <div className="modal-hero__tags">
              {destination.tags?.map(tag => (
                <span key={tag} className="modal-tag">{tag}</span>
              ))}
            </div>
            <h2 className="modal-hero__title">{destination.name}</h2>
            <p className="modal-hero__meta">
              📍{destination.area} · ⭐ {destination.rating}
            </p>
          </div>

          {/* Detail Section */}
          <div className="modal-section">
            <h3>상세 정보</h3>
            <p>{destination.long || destination.short}</p>
          </div>

          {/* Visit Info Section */}
          <div className="modal-section">
            <h3>방문 정보</h3>
            <div className="modal-info-grid">
              <div>
                <strong>전화번호</strong>
                <p>{destination.phone || '정보 없음'}</p>
              </div>
              <div>
                <strong>휴무일</strong>
                <p>{destination.closedDays || '정보 없음'}</p>
              </div>
              <div>
                <strong>운영시간</strong>
                <p>{destination.operatingHours || '정보 없음'}</p>
              </div>
              <div>
                <strong>운영계절</strong>
                <p>{destination.operatingSeason || '정보 없음'}</p>
              </div>
              <div>
                <strong>주차장</strong>
                <p>{destination.parking ? '이용 가능' : '이용 불가'}</p>
              </div>
              <div>
                <strong>유모차</strong>
                <p>{destination.strollerFriendly ? '이용 가능' : '이용 불가'}</p>
              </div>
              <div>
                <strong>반려동물 입장</strong>
                <p>{destination.petFriendly ? '입장 가능' : '입장 불가'}</p>
              </div>
              <div>
                <strong>신용카드</strong>
                <p>{destination.creditCard ? '사용 가능' : '사용 불가'}</p>
              </div>
            </div>
          </div>

          {/* Add to trip controls */}
          <div className="modal-section">
            {trips.length > 0 && (
              <div className="modal-info-grid">
                <div>
                  <strong>추가할 계획 선택</strong>
                  <Select
                    value={selectedTripId}
                    onChange={(value) => setSelectedTripId(value)}
                    options={[{ value: 'NEW', label: '새 여행 계획 만들기' }, ...trips.map(t => ({ value: t.id, label: t.title || '여행 계획' }))]}
                    placeholder="선택하세요"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="destination-modal__actions">
            <Button
              variant="ghost"
              onClick={handleToggleSave}
              type="button"
              disabled={!isAuthenticated}
              title={!isAuthenticated ? '로그인 후 이용해주세요' : ''}
            >
              {isSaved ? '찜 해제' : '찜하기'}
            </Button>
            <Button variant="primary" onClick={handlePlannerAdd} type="button">
              여행 계획에 추가하기
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

export default DestinationDetailModal
