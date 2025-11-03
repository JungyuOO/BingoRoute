import { useState, useCallback, useEffect } from 'react'
import { useStore } from '../../../context/StoreContext'
import { useAuth } from '../../../hooks/api/useAuth'
import { addJjim, removeJjim } from '../../../services/jjimService'
import { fetchTouristSpotDetail } from '../../../services/touristService'
import DestinationDetailModal from './DestinationDetailModal'

const DestinationCard = ({ destination }) => {
  const { wishlist, setWishlist } = useStore()
  const { isAuthenticated, promptLogin, user } = useAuth()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState(null)
  const [detailRequested, setDetailRequested] = useState(false)

  const isSaved = wishlist.includes(destination.id)
  const imageStyle = destination.image
    ? { backgroundImage: `url(${destination.image})`, backgroundSize: 'cover', backgroundPosition: 'center' }
    : undefined

  const toggleSave = useCallback(async (event) => {
    if (event) {
      event.stopPropagation()
    }

    if (!isAuthenticated) {
      promptLogin()
      return
    }

    if (!user?.user_id || isProcessing) {
      return
    }

    setIsProcessing(true)
    try {
      if (isSaved) {
        await removeJjim(user.user_id, destination.id)
        setWishlist(prev => prev.filter(id => id !== destination.id))
      } else {
        await addJjim(user.user_id, destination.id)
        setWishlist(prev => {
          if (prev.includes(destination.id)) {
            return prev
          }
          return [...prev, destination.id]
        })
      }
    } catch (error) {
      console.error('찜 상태 변경 실패:', error)
      alert(error.message || '찜 상태 변경에 실패했습니다.')
    } finally {
      setIsProcessing(false)
    }
  }, [destination.id, isAuthenticated, isSaved, promptLogin, setWishlist, user?.user_id, isProcessing])

  const requestDetail = useCallback(async () => {
    setDetailRequested(true)
    setDetailLoading(true)
    setDetailError(null)
    try {
      const detailData = await fetchTouristSpotDetail(destination.id)
      setDetail(detailData)
    } catch (error) {
      console.error('관광지 상세 정보를 불러오지 못했습니다:', error)
      setDetailError(error.message || '상세 정보를 불러오는 중 문제가 발생했습니다.')
    } finally {
      setDetailLoading(false)
    }
  }, [destination.id])

  useEffect(() => {
    setDetail(null)
    setDetailError(null)
    setDetailRequested(false)
    setDetailLoading(false)
  }, [destination.id])

  useEffect(() => {
    if (!isModalOpen || detail || detailLoading || detailRequested) {
      return
    }
    requestDetail()
  }, [detail, detailLoading, detailRequested, isModalOpen, requestDetail])

  const handleRetryDetail = useCallback(() => {
    setDetail(null)
    setDetailError(null)
    setDetailRequested(false)
  }, [])

  const handleNavigate = useCallback(() => {
    // PlaceView는 더 이상 사용하지 않으므로 이 함수는 빈 함수로 유지
    // 모든 상세 정보는 모달에서 처리됩니다
  }, [])

  const openModal = useCallback(() => {
    setIsModalOpen(true)
  }, [])

  const closeModal = useCallback(() => {
    setIsModalOpen(false)
  }, [])

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
        <div className="img" aria-hidden style={imageStyle} />
        <div className="body">
          <div className="row">
            <strong>{destination.name}</strong>
            {/* <span className="pill">{destination.duration}</span> */}
            <button
              type="button"
              className={`wishlist-toggle ${isSaved ? 'is-saved' : ''}`}
              onClick={toggleSave}
              disabled={isProcessing}
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
            📍{destination.area} · ⭐ {destination.rating}
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
        detail={detail}
        detailLoading={detailLoading}
        detailError={detailError}
        onRetryDetail={handleRetryDetail}
      />
    </>
  )
}

export default DestinationCard
