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

  // Load from localStorage on mount
  useEffect(() => {
    setUsers(JSON.parse(localStorage.getItem('br_users') || '[]'))
    setSession(JSON.parse(localStorage.getItem('br_session') || 'null'))
    setWishlist(JSON.parse(localStorage.getItem('br_wishlist') || '[]'))
    setTrips(JSON.parse(localStorage.getItem('br_trips') || '[]'))
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

  const value = {
    users,
    setUsers,
    session,
    setSession,
    wishlist,
    setWishlist,
    trips,
    setTrips,
    loginRequired,
    setLoginRequired
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
