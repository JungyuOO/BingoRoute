import { useState, useEffect, useMemo, useCallback } from 'react'
import './MyPageView.css'
import '../components/features/destinations/Destinations.css'
import DestinationCard from '../components/features/destinations/DestinationCard'
import TripDetailModal from '../components/features/trips/TripDetailModal'
import { useStore } from '../context/StoreContext'
import { fetchTouristSpots } from '../services/touristService'

const MyPageView = () => {
  const { session, setSession, wishlist, trips, tripsLoading, tripError, removeDestinationFromTrip, deleteTrip, mergeTrips, updateTrip, replanTrip } = useStore()
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
  const [allDestinations, setAllDestinations] = useState([])
  const [destinationsLoading, setDestinationsLoading] = useState(false)
  const [destinationsError, setDestinationsError] = useState(null)

  const neededDestinationIds = useMemo(() => {
    const ids = new Set()
    ;(wishlist || []).forEach(id => ids.add(String(id)))
    ;(trips || []).forEach(trip => {
      (trip.destinations || []).forEach(id => ids.add(String(id)))
    })
    return Array.from(ids)
  }, [wishlist, trips])

  useEffect(() => {
    let cancelled = false

    if (!session?.user_id || neededDestinationIds.length === 0) {
      setAllDestinations([])
      setDestinationsLoading(false)
      setDestinationsError(null)
      return
    }

    const loadDestinations = async () => {
      setDestinationsLoading(true)
      setDestinationsError(null)
      try {
        const results = await Promise.all(
          neededDestinationIds.map(async (id) => {
            try {
              const { items } = await fetchTouristSpots({ content_id: id })
              return items?.[0] || null
            } catch (error) {
              console.error(`관광지(${id}) 정보를 불러오지 못했습니다:`, error)
              return null
            }
          })
        )
        if (!cancelled) {
          setAllDestinations(results.filter(Boolean))
        }
      } catch (error) {
        if (!cancelled) {
          console.error('관광지 목록을 불러오지 못했습니다:', error)
          setDestinationsError(error.message || '관광지 정보를 불러오는 중 오류가 발생했습니다.')
        }
      } finally {
        if (!cancelled) {
          setDestinationsLoading(false)
        }
      }
    }

    loadDestinations()

    return () => {
      cancelled = true
    }
  }, [neededDestinationIds, session?.user_id])

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
    alert('회원정보가 수정되었습니다!') // 아직 백엔드와 연결되지 않은 상태.
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

  const destinationMap = useMemo(() => {
    const map = new Map()
    allDestinations.forEach((d) => {
      if (!d) return
      map.set(String(d.id), d)
      if (d.name) {
        map.set(d.name, d)
      }
    })
    return map
  }, [allDestinations])

  const createPlaceholderDestination = useCallback((id) => ({
    id: String(id),
    name: `관광지 ${id}`,
    area: '정보 없음',
    rating: '정보 없음',
    tags: [],
    short: '상세 정보가 준비되지 않았습니다.',
  }), [])

  const resolveDestination = useCallback(
    (id) => {
      if (id === undefined || id === null) return null
      const match = destinationMap.get(String(id)) || destinationMap.get(id)
      return match || createPlaceholderDestination(id)
    },
    [createPlaceholderDestination, destinationMap]
  )

  const wishlistDestinations = useMemo(() => {
    if (!Array.isArray(wishlist) || wishlist.length === 0) {
      return []
    }
    const uniqueIds = new Set()
    return wishlist.map((rawId) => {
      const key = String(rawId)
      const destination = resolveDestination(key)
      if (!destination) return null
      if (uniqueIds.has(destination.id)) {
        return null
      }
      uniqueIds.add(destination.id)
      return destination
    }).filter(Boolean)
  }, [wishlist, resolveDestination])

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
    const names = (trip.itineraries || []).map(({ content_id: contentId }) => {
      const match = resolveDestination(contentId)
      return match?.name || contentId
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


      {/* 마이페이지 찜한 장소 부분 */}

      <div className="section">
        <h3>찜한 장소 ({wishlist.length})</h3>
        {destinationsLoading ? (
          <div className="center">
            <p className="muted">찜한 장소를 불러오는 중입니다...</p>
          </div>
        ) : destinationsError ? (
          <div className="center">
            <p className="muted" style={{ color: 'red' }}>{destinationsError}</p>
          </div>
        ) : wishlistDestinations.length > 0 ? (
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
          <div className="merge-row">
            <span className="merge-label">계획 병합</span>
            <select className="form-input merge-select" value={mergeTarget} onChange={(e) => setMergeTarget(e.target.value)}>
              <option value="">대상 선택</option>
              {trips.map(t => <option key={t.id} value={t.id}>{t.title || '여행 계획'}</option>)}
            </select>
            <span>⬅︎</span>
            <select className="form-input merge-select" value={mergeSource} onChange={(e) => setMergeSource(e.target.value)}>
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


        {/* 여행계획 리스트부분! 
        (버튼형식이라 클릭하면 여행경로 및 세부정보 모달창이 뜨도록 설계됨) */}

        {tripError ? (
          <div className="center">
            <p className="muted" style={{ color: 'red' }}>{tripError.message || '여행 계획을 불러오지 못했습니다.'}</p>
          </div>
        ) : tripsLoading ? (
          <div className="center">
            <p className="muted">여행 계획을 불러오는 중입니다...</p>
          </div>
        ) : trips.length > 0 ? (
          <div className="trip-list">
            {trips
              .slice()
              .sort((a, b) => {
                const statusA = getTripStatus(a)
                const statusB = getTripStatus(b)

                // 여행 상태 우선순위: 여행중(1) > 예정(2) > 완료(3) 순으로 정렬됨.
                const getPriority = (status) => {
                  if (status === '여행중') return 1
                  if (status === '예정') return 2
                  if (status === '완료') return 3
                  return 4 // 상태가 없는 경우
                }

                return getPriority(statusA) - getPriority(statusB)
              })
              .map((trip, index) => (
                <div
                  key={index}
                  className="trip-button"
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
                    <div className="status-container">
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
                      {(trip.itineraries || []).length > 0 ? (
                        (trip.itineraries || []).map((itinerary, i) => {
                          const dest = resolveDestination(itinerary.content_id)
                          return (
                            <span key={`${itinerary.content_id}-${itinerary.seq}-${i}`} className="destination-tag destination-tag-editable">
                              {dest?.name || itinerary.content_id}
                              {editingTripId === trip.id && (
                                <button
                                  className="btn-cancel destination-remove-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    e.preventDefault();
                                    removeDestinationFromTrip(trip.id, itinerary.seq)
                                  }}
                                >
                                  ×
                                </button>
                              )}
                            </span>
                          )
                        })
                      ) : (
                        <span className="weather-message-small">경로 없음</span>
                      )}
                    </div>
                    <div className="trip-actions-row">
                      <button className="btn-edit" onClick={(e) => { e.stopPropagation(); setEditingTripId(editingTripId === trip.id ? null : trip.id) }}>{editingTripId === trip.id ? '수정 완료' : '수정하기'}</button>
                      <button className="btn-share" onClick={(e) => { e.stopPropagation(); shareTrip(trip) }}>공유하기</button>
                      {getTripStatus(trip) === '완료' && (
                        <button
                          className="btn-replan"
                          onClick={(e) => {
                            e.stopPropagation();
                            replanTrip(trip.id);
                            alert('여행 계획이 다시 계획되었습니다! 새로운 날짜를 설정해보세요.');
                          }}
                        >
                          다시 계획하기
                        </button>
                      )}
                    </div>
                    {editingTripId === trip.id && (
                      <div className="delete-actions" onClick={(e) => e.stopPropagation()}>
                        <button className="btn-cancel" onClick={(e) => { e.stopPropagation(); deleteTrip(trip.id) }}>여행 삭제</button>
                      </div>
                    )}
                    {editingTripId === trip.id && (
                      <div className="edit-trip-form" onClick={(e) => e.stopPropagation()}>
                        <label className="trip-title-label">
                          여행명
                          <input
                            type="text"
                            value={trip.title || ''}
                            placeholder="여행명을 입력하세요"
                            className="form-input"
                            onClick={(e) => e.stopPropagation()}
                            onMouseDown={(e) => e.stopPropagation()}
                            onFocus={(e) => e.stopPropagation()}
                            onChange={(e) => updateTrip(trip.id, { title: e.target.value })}
                          />
                        </label>
                        <div className="dates-row">
                          <label className="date-label">
                            시작일
                            <input
                              type="date"
                              value={trip.startDate || ''}
                              onClick={(e) => e.stopPropagation()}
                              onMouseDown={(e) => e.stopPropagation()}
                              onFocus={(e) => e.stopPropagation()}
                              onChange={(e) => updateTrip(trip.id, { startDate: e.target.value })}
                            />
                          </label>
                          <label className="date-label">
                            종료일
                            <input
                              type="date"
                              value={trip.endDate || ''}
                              onClick={(e) => e.stopPropagation()}
                              onMouseDown={(e) => e.stopPropagation()}
                              onFocus={(e) => e.stopPropagation()}
                              onChange={(e) => updateTrip(trip.id, { endDate: e.target.value })}
                            />
                          </label>
                        </div>
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

      <TripDetailModal
        trip={selectedTrip}
        isOpen={isTripModalOpen}
        onClose={closeTripModal}
        resolveDestination={resolveDestination}
      />
    </div>
  )
}

export default MyPageView
