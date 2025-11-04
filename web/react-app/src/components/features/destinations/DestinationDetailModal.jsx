import { useState } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '../../ui'
import { useAuth } from '../../../hooks/api/useAuth'
import { useStore } from '../../../context/StoreContext'
import './DestinationDetailModal.css'

const DestinationDetailModal = ({
  destination,
  isOpen,
  onClose,
  isSaved,
  onToggleSave,
  detail,
  detailLoading = false,
  detailError = null,
  onRetryDetail,
}) => {
  const { isAuthenticated, promptLogin } = useAuth()
  const [showPlanModal, setShowPlanModal] = useState(false)
  const { addDestinationToTrip, trips } = useStore()

  // 🔹 로그인 안 돼있으면 로그인 유도
  const handlePlannerAdd = () => {
    if (!isAuthenticated) {
      promptLogin()
      return
    }
    setShowPlanModal(true) // ✅ 여행 계획 선택창만 띄움
  }

  // 🔹 모달 닫기
  const handleBackdropClick = () => onClose()
  const handleContentClick = (event) => event.stopPropagation()

  // 🔹 여행계획 선택 시 실행
  const handleSelectPlan = async (planId) => {
    const selectedPlan = trips.find(p => p.id === Number(planId))
    if (!selectedPlan) return alert('선택한 여행 계획을 찾을 수 없습니다.')

    try {
      await addDestinationToTrip({ tripId: selectedPlan.id, destination })
      alert(`"${selectedPlan.title}" 여행 계획에 "${destination.name}"이(가) 추가되었습니다!`)
      setShowPlanModal(false)
    } catch (error) {
      console.error('여행 계획에 추가하지 못했습니다:', error)
      alert('여행 계획에 추가하지 못했습니다. 잠시 후 다시 시도해주세요.')
    }
  }

  // 🔹 새 여행 계획 생성
  const handleCreateNewPlan = async () => {
    const title = prompt('새 여행 계획의 이름을 입력하세요 ✏️')
    if (!title) return
    try {
      await addDestinationToTrip({ tripTitle: title, destination })
      alert(`"${title}" 여행 계획이 생성되고 "${destination.name}"이(가) 추가되었습니다!`)
      setShowPlanModal(false)
      onClose()
    } catch (error) {
      console.error('새 여행 계획을 생성하지 못했습니다:', error)
      alert('새 여행 계획을 만들지 못했습니다. 잠시 후 다시 시도해주세요.')
    }
  }

  if (!isOpen || typeof document === 'undefined') return null
  const modalRoot = document.getElementById('modal-root') || document.body
  const heroImage = destination?.raw?.firstimage || destination?.raw?.firstimage2 || destination?.image || null

  return createPortal(
    (
      <div
        className="destination-modal__backdrop"
        onClick={handleBackdropClick}
      >
        <div className="destination-modal" role="dialog" aria-modal="true" onClick={handleContentClick}>
          <div className="destination-modal__header">
            <button
              type="button"
              className="destination-modal__close"
              onClick={onClose}
              aria-label="닫기"
            >
              ×
            </button>
          </div>

          <div className="destination-modal__content">
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
                {destination.tags?.map(tag => (
                  <span key={tag} className="modal-tag">{tag}</span>
                ))}
              </div>
              <h2 className="modal-hero__title">{destination.name}</h2>
              <p className="modal-hero__meta">
                📍{destination.area} · ⭐ {destination.rating}
              </p>
            </div>

            <div className="modal-section">
              <h3>상세 정보</h3>
              {detailLoading ? (
                <p>상세 정보를 불러오는 중입니다...</p>
              ) : detailError ? (
                <div>
                  <p style={{ color: 'red', marginBottom: '8px' }}>{detailError}</p>
                  {typeof onRetryDetail === 'function' && (
                    <Button variant="ghost" onClick={onRetryDetail}>
                      다시 시도
                    </Button>
                  )}
                </div>
              ) : (
                <p>{detail?.description || destination.long || destination.short}</p>
              )}
            </div>

            <div className="modal-section">
              <h3>방문 정보</h3>
              <div className="modal-info-grid">
                <div><strong>주소</strong><p>{detail?.address || destination.area || '정보 없음'}</p></div>
                <div><strong>전화번호</strong><p>{detail?.tel || '정보 없음'}</p></div>
                <div><strong>휴무일</strong><p>{detail?.restdate || '정보 없음'}</p></div>
                <div><strong>운영시간</strong><p>{detail?.usetime || '정보 없음'}</p></div>
                <div><strong>운영계절</strong><p>{detail?.useseason || '정보 없음'}</p></div>
                <div><strong>주차장</strong><p>{detail?.facilities?.parking ? '이용 가능' : '이용 불가'}</p></div>
                <div><strong>유모차</strong><p>{detail?.facilities?.babyCarriage ? '이용 가능' : '이용 불가'}</p></div>
                <div><strong>반려동물 입장</strong><p>{detail?.facilities?.pet ? '입장 가능' : '입장 불가'}</p></div>
                <div><strong>신용카드</strong><p>{detail?.facilities?.creditCard ? '사용 가능' : '사용 불가'}</p></div>
              </div>
            </div>

            <div className="destination-modal__actions">
              <Button variant="ghost" onClick={onToggleSave}>
                {isSaved ? '찜 해제' : '찜하기'}
              </Button>
              <Button variant="primary" onClick={handlePlannerAdd}>
                여행 계획에 추가하기
              </Button>
            </div>
          </div>
        </div>

        {/* ✅ 여행 계획 선택 모달 */}
        {showPlanModal && (
          <div className="plan-select-modal__backdrop" onClick={() => setShowPlanModal(false)}>
            <div className="plan-select-modal" onClick={(e) => e.stopPropagation()}>
              <h3>여행 계획에 추가하기</h3>
              {trips.length > 0 ? (
                <select
                  className="dropdown-select"
                  onChange={(e) => handleSelectPlan(e.target.value)}
                  defaultValue="none"
                >
                  <option value="none" disabled>여행 계획을 선택하세요</option>
                  {trips.map(plan => (
                    <option key={plan.id} value={plan.id}>{plan.title}</option>
                  ))}
                </select>
              ) : (
                <p>저장된 여행 계획이 없습니다.</p>
              )}
              <Button
                variant="primary"
                onClick={handleCreateNewPlan}
                className="create-plan-button"
              >
                + 새 여행 계획 만들기
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowPlanModal(false)}
                className="close-button"
              >
                닫기
              </Button>
            </div>
          </div>
        )}
      </div>
    ),
    modalRoot
  )
}

export default DestinationDetailModal
