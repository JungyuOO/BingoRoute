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
  // UI states
  const [loginRequired, setLoginRequired] = useState(false)

  // helpers
  const genId = () => `trip_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`

  const ensureTripIds = (items) => {
    return (items || []).map(t => ({ id: t.id || genId(), destinations: t.destinations || t.routes || [], ...t }))
  }

  // Load from localStorage on mount
  useEffect(() => {
    setUsers(JSON.parse(localStorage.getItem('br_users') || '[]'))
    setSession(JSON.parse(localStorage.getItem('br_session') || 'null'))
    setWishlist(JSON.parse(localStorage.getItem('br_wishlist') || '[]'))
    const storedTrips = JSON.parse(localStorage.getItem('br_trips') || '[]')
    setTrips(ensureTripIds(storedTrips))
  }, [])

  // No backend session hydration; JWT is stored in session as `access`

  // Save to localStorage when state changes
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

  // Trip operations
  const createTripWithDestination = (destinationIdOrName, defaults = {}) => {
    const trip = {
      id: genId(),
      title: `${defaults.title || destinationIdOrName} 나들이`,
      date: defaults.date ?? null,
      duration: defaults.duration || '당일치기',
      style: defaults.style || '관광',
      budget: defaults.budget || '미정',
      companions: defaults.companions || '미정',
      destinations: [destinationIdOrName],
      createdAt: new Date().toISOString(),
    }
    setTrips(prev => [trip, ...prev])
    return trip.id
  }

  const appendDestinationToTrip = (tripId, destinationIdOrName) => {
    setTrips(prev => prev.map(t => {
      if (t.id !== tripId) return t
      const exists = (t.destinations || []).some(x => x === destinationIdOrName)
      return exists ? t : { ...t, destinations: [...(t.destinations || []), destinationIdOrName] }
    }))
  }

  const removeDestinationFromTrip = (tripId, destinationIdOrName) => {
    setTrips(prev => prev.map(t => t.id === tripId ? { ...t, destinations: (t.destinations || []).filter(x => x !== destinationIdOrName) } : t))
  }

  const deleteTrip = (tripId) => {
    setTrips(prev => prev.filter(t => t.id !== tripId))
  }

  const mergeTrips = (targetTripId, sourceTripIds = []) => {
    setTrips(prev => {
      const target = prev.find(t => t.id === targetTripId)
      if (!target) return prev
      const others = prev.filter(t => t.id !== targetTripId)
      const toMerge = others.filter(t => sourceTripIds.includes(t.id))
      const mergedDest = Array.from(new Set([...(target.destinations || []), ...toMerge.flatMap(t => t.destinations || [])]))
      const kept = others.filter(t => !sourceTripIds.includes(t.id))
      return [{ ...target, destinations: mergedDest }, ...kept]
    })
  }

  const updateTrip = (tripId, patch) => {
    setTrips(prev => prev.map(t => t.id === tripId ? { ...t, ...patch } : t))
  }

  const value = {
    users,
    setUsers,
    session,
    setSession,
    wishlist,
    setWishlist,
    trips,
    setTrips,
    createTripWithDestination,
    appendDestinationToTrip,
    removeDestinationFromTrip,
    deleteTrip,
    mergeTrips,
    updateTrip,
    loginRequired,
    setLoginRequired
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
