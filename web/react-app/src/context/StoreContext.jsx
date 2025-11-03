import { createContext, useContext, useState, useEffect } from 'react'

const StoreContext = createContext()

export const useStore = () => {
  const context = useContext(StoreContext)
  if (!context) {
    throw new Error('useStore must be used within a StoreProvider')
  }
  return context
}

export const StoreProvider = ({ children }) => {
  const [users, setUsers] = useState([])
  const [session, setSession] = useState(null)
  const [wishlist, setWishlist] = useState([])
  const [trips, setTrips] = useState([])
  const [loginRequired, setLoginRequired] = useState(false)

  // API 기본 URL
  const API_BASE_URL = 'http://localhost:8000/api'

  // 찜하기 토글 함수 (임시로 로컬스토리지 기반으로 작동)
  const toggleWishlist = async (contentId) => {
    console.log('🔄 toggleWishlist 호출됨:', { contentId, session, wishlist })
    
    if (!session) {
      console.log('❌ 세션 없음, 로그인 필요')
      setLoginRequired(true)
      return false
    }

    // 임시로 로컬스토리지 기반으로 작동
    const isCurrentlySaved = wishlist.includes(contentId)
    console.log('📋 현재 찜 상태:', isCurrentlySaved)
    
    if (isCurrentlySaved) {
      // 찜 해제
      console.log('🗑️ 찜 해제 (로컬)')
      setWishlist(prev => prev.filter(id => id !== contentId))
      return false
    } else {
      // 찜 추가
      console.log('❤️ 찜 추가 (로컬)')
      setWishlist(prev => [...prev, contentId])
      return true
    }

    // TODO: 나중에 API 연동
    /*
    try {
      const isCurrentlySaved = wishlist.includes(contentId)
      console.log('📋 현재 찜 상태:', isCurrentlySaved)
      
      if (isCurrentlySaved) {
        // 찜 해제
        console.log('🗑️ 찜 해제 요청 중...')
        const response = await fetch(`${API_BASE_URL}/service/jjim/?user_id=${session.user_id}&content_id=${contentId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        console.log('🗑️ 찜 해제 응답:', response.status, response.ok)
        
        if (response.ok) {
          setWishlist(prev => prev.filter(id => id !== contentId))
          console.log('✅ 찜 해제 완료')
          return false
        } else {
          const errorData = await response.text()
          console.error('❌ 찜 해제 실패:', errorData)
        }
      } else {
        // 찜 추가
        console.log('❤️ 찜 추가 요청 중...')
        const response = await fetch(`${API_BASE_URL}/service/jjim/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: session.user_id,
            content_id: contentId
          })
        })

        console.log('❤️ 찜 추가 응답:', response.status, response.ok)
        
        if (response.ok) {
          setWishlist(prev => [...prev, contentId])
          console.log('✅ 찜 추가 완료')
          return true
        } else {
          const errorData = await response.text()
          console.error('❌ 찜 추가 실패:', errorData)
        }
      }
    } catch (error) {
      console.error('❌ 찜하기 API 오류:', error)
    }
    
    return false
    */
  }

  // 찜 목록 불러오기
  const loadWishlist = async () => {
    if (!session) return

    try {
      const response = await fetch(`${API_BASE_URL}/service/jjim/?user_id=${session.user_id}`)

      if (response.ok) {
        const data = await response.json()
        setWishlist(data.content_id || [])
      }
    } catch (error) {
      console.error('찜 목록 불러오기 오류:', error)
    }
  }

  // 세션이 변경될 때 찜 목록 로드
  useEffect(() => {
    if (session) {
      loadWishlist()
    } else {
      setWishlist([])
    }
  }, [session])
  // 여행 계획에 여행지 추가하는 함수 (중복 제거 + 통합버전)
  const addDestinationToTrip = (tripTitle, destinationName) => {
    setTrips((prevTrips) => {
      const existingTrip = prevTrips.find((t) => t.title === tripTitle)

      if (existingTrip) {
        // 이미 같은 장소가 있으면 중복 추가 방지
        if (existingTrip.destinations.includes(destinationName)) return prevTrips

        // 기존 계획에 추가
        return prevTrips.map((t) =>
          t.title === tripTitle
            ? { ...t, destinations: [...t.destinations, destinationName] }
            : t
        )
      } else {
        // 새로운 여행 계획 생성
        const newTrip = {
          id: Date.now(),
          title: tripTitle,
          date: new Date().toISOString().slice(0, 10),
          destinations: [destinationName],
          startDate: null,
          endDate: null,
        }
        return [...prevTrips, newTrip]
      }
    })
  }

  // 전체 여행 계획 삭제
  const clearTrips = () => setTrips([])

  // 여행 계획 업데이트 (날짜 등)
  const updateTrip = (tripId, updates) => {
    setTrips((prevTrips) =>
      prevTrips.map((trip) =>
        trip.id === tripId ? { ...trip, ...updates } : trip
      )
    )
  }

  // 여행 계획에서 여행지 제거
  const removeDestinationFromTrip = (tripId, destinationName) => {
    setTrips((prevTrips) =>
      prevTrips.map((trip) =>
        trip.id === tripId
          ? {
            ...trip,
            destinations: trip.destinations.filter((d) => d !== destinationName),
          }
          : trip
      )
    )
  }

  // 여행 계획 삭제
  const deleteTrip = (tripId) => {
    setTrips((prevTrips) => prevTrips.filter((trip) => trip.id !== tripId))
  }

  // 여행 계획 병합
  const mergeTrips = (targetTripId, sourceTripIds) => {
    setTrips((prevTrips) => {
      const targetTrip = prevTrips.find((trip) => trip.id === targetTripId)
      const sourceTrips = prevTrips.filter((trip) => sourceTripIds.includes(trip.id))

      if (!targetTrip || sourceTrips.length === 0) return prevTrips

      // 모든 여행지를 병합 (중복 제거)
      const allDestinations = [
        ...(targetTrip.destinations || []),
        ...sourceTrips.flatMap((trip) => trip.destinations || []),
      ]
      const uniqueDestinations = [...new Set(allDestinations)]

      // 대상 여행 계획 업데이트 및 소스 여행 계획들 제거
      return prevTrips
        .filter((trip) => !sourceTripIds.includes(trip.id))
        .map((trip) =>
          trip.id === targetTripId
            ? { ...trip, destinations: uniqueDestinations }
            : trip
        )
    })
  }

  // 완료된 여행 계획을 다시 계획하기 (날짜 초기화)
  const replanTrip = (tripId) => {
    setTrips((prevTrips) =>
      prevTrips.map((trip) =>
        trip.id === tripId
          ? {
            ...trip,
            startDate: null,
            endDate: null,
            title: `${trip.title} (재계획)`,
          }
          : trip
      )
    )
  }

  // --- LocalStorage 동기화 ---
  useEffect(() => {
    setUsers(JSON.parse(localStorage.getItem('br_users') || '[]'))
    setSession(JSON.parse(localStorage.getItem('br_session') || 'null'))
    setWishlist(JSON.parse(localStorage.getItem('br_wishlist') || '[]'))
    const storedTrips = JSON.parse(localStorage.getItem('br_trips') || '[]')
    setTrips(storedTrips)
  }, [])

  // 로컬스토리지에 자동 저장
  useEffect(() => {
    localStorage.setItem('br_users', JSON.stringify(users))
  }, [users])

  useEffect(() => {
    if (session === null) {
      localStorage.removeItem('br_session')
    } else {
      localStorage.setItem('br_session', JSON.stringify(session))
    }
  }, [session])

  useEffect(() => {
    localStorage.setItem('br_wishlist', JSON.stringify(wishlist))
  }, [wishlist])

  useEffect(() => {
    localStorage.setItem('br_trips', JSON.stringify(trips))
  }, [trips])

  // value 객체에 함수 포함
  const value = {
    users,
    setUsers,
    session,
    setSession,
    wishlist,
    setWishlist,
    trips,
    setTrips,
    addDestinationToTrip, // 👈 여행지 추가 함수
    clearTrips, // 👈 전체 삭제 함수
    updateTrip, // 👈 여행 계획 업데이트 함수
    removeDestinationFromTrip, // 👈 여행지 제거 함수
    deleteTrip, // 👈 여행 계획 삭제 함수
    mergeTrips, // 👈 여행 계획 병합 함수
    replanTrip, // 👈 여행 다시 계획하기 함수
    loginRequired,
    setLoginRequired,
    toggleWishlist, // 👈 찜하기 토글 함수
    loadWishlist, // 👈 찜 목록 불러오기 함수
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
