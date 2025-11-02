import { useState, useEffect } from 'react'
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
}) => {
  const { isAuthenticated, promptLogin } = useAuth()
  const [showPlanModal, setShowPlanModal] = useState(false)
  const { addDestinationToTrip, trips } = useStore()
  const [destinationDetails, setDestinationDetails] = useState(null)
  const [loadingDetails, setLoadingDetails] = useState(false)

  // 🔹 상세 정보 API 호출
  useEffect(() => {
    if (isOpen && destination?.id) {
      const fetchDestinationDetails = async () => {
        try {
          setLoadingDetails(true)
          console.log('🔄 관광지 상세정보 요청:', destination.id)
          const response = await fetch(`http://localhost:8000/api/service/tourist_spots/detail/${destination.id}/`)
          const data = await response.json()
          console.log('📊 상세정보 API 응답:', { status: response.status, data })

          if (response.ok && data.results && Array.isArray(data.results)) {
            // 상세 정보를 객체로 변환 (TouristDetail 테이블 필드명 사용)
            const details = {}
            
            // 여러 레코드에서 정보를 수집 (같은 content_id에 대해 여러 상세정보가 있을 수 있음)
            data.results.forEach(item => {
              // 기본 정보
              if (item.tel) details.phone = item.tel
              if (item.restdate) details.closedDays = item.restdate
              if (item.usetime) details.operatingHours = item.usetime
              if (item.useseason) details.operatingSeason = item.useseason
              if (item.address) details.address = item.address
              
              // 편의시설 정보 (문자열 '1' 또는 '0'으로 저장됨)
              if (item.is_parking) details.parking = item.is_parking === '1' || item.is_parking === 1
              if (item.is_baby_carriage) details.strollerFriendly = item.is_baby_carriage === '1' || item.is_baby_carriage === 1
              if (item.is_pet) details.petFriendly = item.is_pet === '1' || item.is_pet === 1
              if (item.is_credit_card) details.creditCard = item.is_credit_card === '1' || item.is_credit_card === 1
              
              // 추가 정보 텍스트
              if (item.info_text) {
                if (!details.descriptions) details.descriptions = []
                details.descriptions.push({
                  name: item.info_name || '정보',
                  text: item.info_text
                })
              }
            })
            
            setDestinationDetails(details)
            console.log('✅ 상세정보 로드 완료:', details)
          } else {
            console.log('❌ 상세정보 응답 형식 오류:', data)
          }
        } catch (error) {
          console.error('⚠️ 관광지 상세정보 API 요청 오류:', error)
        } finally {
          setLoadingDetails(false)
        }
      }

      fetchDestinationDetails()
    }
  }, [isOpen, destination?.id])

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
  const handleSelectPlan = (planId) => {
    const selectedPlan = trips.find(p => p.id === Number(planId))
    if (!selectedPlan) return alert('선택한 여행 계획을 찾을 수 없습니다.')

    addDestinationToTrip(selectedPlan.title, destination.name)
    alert(`"${selectedPlan.title}" 여행 계획에 "${destination.name}"이(가) 추가되었습니다!`)
    setShowPlanModal(false)
  }

  // 🔹 새 여행 계획 생성
  const handleCreateNewPlan = () => {
    const title = prompt('새 여행 계획의 이름을 입력하세요 ✏️')
    if (!title) return
    addDestinationToTrip(title, destination.name)
    alert(`"${title}" 여행 계획이 생성되고 "${destination.name}"이(가) 추가되었습니다!`)
    setShowPlanModal(false)
    onClose()
  }

  if (!isOpen || typeof document === 'undefined') {
    console.log('🚫 모달 렌더링 조건:', { isOpen, hasDocument: typeof document !== 'undefined' })
    return null
  }

  console.log('✅ 모달 렌더링 중:', destination?.name)
  const modalRoot = document.getElementById('modal-root') || document.body

  return createPortal(
    <>
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
            <div className="modal-hero">
              {destination.image && (
                <div className="modal-hero__image">
                  <img 
                    src={destination.image} 
                    alt={destination.name}
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                </div>
              )}
              <div className="modal-hero__tags">
                {destination.tags?.map(tag => (
                  <span key={tag} className="modal-tag">{tag}</span>
                ))}
              </div>
              <h2 className="modal-hero__title">{destination.name}</h2>
              <p className="modal-hero__meta">
                📍{destinationDetails?.area || destination.area}
                {destination.rating && ` · ⭐ ${destination.rating}`}
              </p>
            </div>

            <div className="modal-section">
              <h3>상세 정보</h3>
              {loadingDetails ? (
                <p>상세 정보를 불러오는 중...</p>
              ) : (
                <>
                  {destinationDetails?.descriptions && destinationDetails.descriptions.length > 0 ? (
                    destinationDetails.descriptions.map((desc, index) => (
                      <div key={index} style={{ marginBottom: '1rem' }}>
                        <h4 style={{ fontSize: '0.9rem', color: '#5EABA2', marginBottom: '0.5rem' }}>
                          {desc.name}
                        </h4>
                        <p>{desc.text}</p>
                      </div>
                    ))
                  ) : (
                    <p>{destination.long || destination.short}</p>
                  )}
                  {destinationDetails?.address && (
                    <p><strong>주소:</strong> {destinationDetails.address}</p>
                  )}
                </>
              )}
            </div>

            <div className="modal-section">
              <h3>방문 정보</h3>
              {loadingDetails ? (
                <p>방문 정보를 불러오는 중...</p>
              ) : (
                <div className="modal-info-grid">
                  <div><strong>전화번호</strong><p>{destinationDetails?.phone || '정보 없음'}</p></div>
                  <div><strong>휴무일</strong><p>{destinationDetails?.closedDays || '정보 없음'}</p></div>
                  <div><strong>운영시간</strong><p>{destinationDetails?.operatingHours || '정보 없음'}</p></div>
                  <div><strong>운영계절</strong><p>{destinationDetails?.operatingSeason || '정보 없음'}</p></div>
                  <div><strong>주차장</strong><p>{destinationDetails?.parking !== undefined ? (destinationDetails.parking ? '이용 가능' : '이용 불가') : '정보 없음'}</p></div>
                  <div><strong>유모차</strong><p>{destinationDetails?.strollerFriendly !== undefined ? (destinationDetails.strollerFriendly ? '이용 가능' : '이용 불가') : '정보 없음'}</p></div>
                  <div><strong>반려동물 입장</strong><p>{destinationDetails?.petFriendly !== undefined ? (destinationDetails.petFriendly ? '입장 가능' : '입장 불가') : '정보 없음'}</p></div>
                  <div><strong>신용카드</strong><p>{destinationDetails?.creditCard !== undefined ? (destinationDetails.creditCard ? '사용 가능' : '사용 불가') : '정보 없음'}</p></div>
                </div>
              )}
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
    </>,
    modalRoot
  )
}

export default DestinationDetailModal