import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from "../../../hooks/api/useAuth";



const RequireAuth = ({ children }) => {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  // ⭐ 특정 경로는 로그인 없이 접근 허용
  const publicPaths = ['/planner']

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return children
}

export default RequireAuth