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

  // ✅ 여행 계획에 여행지 추가하는 함수 (중복 제거 + 통합버전)
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

  // ✅ 전체 여행 계획 삭제
  const clearTrips = () => setTrips([])

  // --- LocalStorage 동기화 ---
  useEffect(() => {
    setUsers(JSON.parse(localStorage.getItem('br_users') || '[]'))
    setSession(JSON.parse(localStorage.getItem('br_session') || 'null'))
    setWishlist(JSON.parse(localStorage.getItem('br_wishlist') || '[]'))
    setTrips(JSON.parse(localStorage.getItem('br_trips') || '[]'))
  }, [])

  // ✅ 로컬스토리지에 자동 저장
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

  // ✅ value 객체에 함수 포함
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
    loginRequired,
    setLoginRequired,
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
