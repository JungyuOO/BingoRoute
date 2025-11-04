import { createContext, useContext, useState, useEffect } from 'react'
import { fetchJjimList } from '../services/jjimService'
import { validateSession } from '../services/authService'

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
  const [storageHydrated, setStorageHydrated] = useState(false)
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
    let cancelled = false

    const hydrateFromStorage = async () => {
      const storedUsers = JSON.parse(localStorage.getItem('br_users') || '[]')
      const storedWishlist = JSON.parse(localStorage.getItem('br_wishlist') || '[]')
      const storedTrips = JSON.parse(localStorage.getItem('br_trips') || '[]')
      const storedSession = JSON.parse(localStorage.getItem('br_session') || 'null')

      if (!cancelled) {
        setUsers(storedUsers)
        setWishlist(storedWishlist)
        setTrips(storedTrips)
      }

      if (storedSession?.access) {
        try {
          const data = await validateSession(storedSession.access)
          if (!cancelled) {
            setSession({ ...data.user, access: storedSession.access })
          }
        } catch (error) {
          if (cancelled) return
          if (error?.status === 401) {
            console.warn('Stored session is no longer valid. Clearing it.', error)
            setSession(null)
            localStorage.removeItem('br_session')
          } else {
            console.warn('Unable to verify stored session. Keeping cached session for now.', error)
            setSession(storedSession)
          }
        }
      } else if (!cancelled) {
        setSession(storedSession)
      }

      if (!cancelled) {
        setStorageHydrated(true)
      }
    }

    hydrateFromStorage()

    return () => {
      cancelled = true
    }
  }, [])

  // 로컬스토리지에 자동 저장
  useEffect(() => {
    if (!storageHydrated) return
    localStorage.setItem('br_users', JSON.stringify(users))
  }, [users, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    if (session === null) {
      localStorage.removeItem('br_session')
    } else {
      localStorage.setItem('br_session', JSON.stringify(session))
    }
  }, [session, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    localStorage.setItem('br_wishlist', JSON.stringify(wishlist))
  }, [wishlist, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    localStorage.setItem('br_trips', JSON.stringify(trips))
  }, [trips, storageHydrated])

  useEffect(() => {
    let cancelled = false

    const syncWishlist = async () => {
      if (!session?.user_id) {
        setWishlist([])
        return
      }
      try {
        const remoteWishlist = await fetchJjimList(session.user_id)
        if (!cancelled) {
          setWishlist(remoteWishlist)
        }
      } catch (error) {
        console.error('찜 목록을 불러오지 못했습니다:', error)
      }
    }

    syncWishlist()

    return () => {
      cancelled = true
    }
  }, [session?.user_id])

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
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
