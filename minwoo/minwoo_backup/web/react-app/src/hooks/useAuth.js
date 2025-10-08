import { useStore } from '../context/StoreContext'

export const useAuth = () => {
  const { session, setSession, setLoginRequired } = useStore()

  const login = (user) => {
    setSession(user)
  }

  const logout = async () => {
    setSession(null)
  }

  const isAuthenticated = !!session

  const promptLogin = () => setLoginRequired(true)

  return {
    user: session,
    login,
    logout,
    isAuthenticated,
    promptLogin
  }
}
