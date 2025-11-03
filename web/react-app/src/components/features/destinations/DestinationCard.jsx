import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../../../context/StoreContext'
import { useAuth } from "../../../hooks/api/useAuth"
import DestinationDetailModal from './DestinationDetailModal'

const DestinationCard = ({ destination }) => {
  const { wishlist, toggleWishlist } = useStore()
  const { isAuthenticated, promptLogin } = useAuth()
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)

  const isSaved = wishlist.includes(destination.id)

  const toggleSave = useCallback(async (event) => {
    console.log('🖱️ 찜하기 버튼 클릭됨:', destination.name, destination.id)
    
    if (event) {
      event.stopPropagation()
    }

    if (!isAuthenticated) {
      console.log('❌ 인증되지 않음, 로그인 프롬프트 표시')
      promptLogin()
      return
    }

    console.log('🔄 toggleWishlist 호출 시작')
    // API를 통해 찜하기 토글
    const result = await toggleWishlist(destination.id)
    console.log('✅ toggleWishlist 완료:', result)
  }, [destination.id, destination.name, isAuthenticated, promptLogin, toggleWishlist])

  const handleNavigate = useCallback(() => {
    // PlaceView는 더 이상 사용하지 않으므로 이 함수는 빈 함수로 유지
    // 모든 상세 정보는 모달에서 처리됩니다
  }, [])

  const openModal = useCallback(() => {
    console.log('🔓 모달 열기:', destination.name)
    setIsModalOpen(true)
  }, [destination.name])

  const closeModal = useCallback(() => {
    console.log('🔒 모달 닫기:', destination.name)
    setIsModalOpen(false)
  }, [destination.name])

  const handleKeyDown = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      openModal()
    }
  }, [openModal])

  return (
    <>
      <div
        className="card card-interactive"
        role="button"
        tabIndex={0}
        onClick={openModal}
        onKeyDown={handleKeyDown}
      >
        <div className="img" aria-hidden>
          {destination.image ? (
            <>
              <img
                src={destination.image}
                alt={destination.name}
                loading="lazy"
                onError={(e) => {
                  // 이미지 로딩 실패 시 숨기기
                  e.target.style.display = 'none'
                }}
              />
              <div className="img-placeholder" />
            </>
          ) : (
            <div className="img-placeholder" />
          )}
        </div>
        <div className="body">
          <div className="row">
            <strong>{destination.name}</strong>
            {/* <span className="pill">{destination.duration}</span> */}
            <button
              type="button"
              className={`wishlist-toggle ${isSaved ? 'is-saved' : ''}`}
              onClick={toggleSave}
              aria-pressed={isSaved}
              aria-label={isSaved ? '찜 해제' : '찜하기'}
              title={isSaved ? '찜 해제' : '찜하기'}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path d="M12 21.35 10.55 20.03C5.4 15.36 2 12.27 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.77-3.4 6.86-8.55 11.54L12 21.35Z" />
              </svg>
            </button>
          </div>
          <div className="meta">
            📍{destination.area}
            {destination.rating && ` · ⭐ ${destination.rating}`}
          </div>
          <p className="muted">{destination.short}</p>
        </div>
      </div>

      <DestinationDetailModal
        destination={destination}
        isOpen={isModalOpen}
        onClose={closeModal}
        onNavigate={handleNavigate}
        isSaved={isSaved}
        onToggleSave={toggleSave}
      />
    </>
  )
}

export default DestinationCard
