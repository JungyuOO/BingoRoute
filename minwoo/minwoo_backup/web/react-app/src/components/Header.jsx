import "../styles/header.css";
import logo from "../assets/BingoRoute.jpeg";
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ROUTES } from '../router/routes'

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const location = useLocation()
  const HIDE_SEARCH_PREFIXES = [ROUTES.PLANNER, ROUTES.LOGIN, ROUTES.SIGNUP, ROUTES.MYPAGE]
  const hideSearch = HIDE_SEARCH_PREFIXES.some(prefix => location.pathname.startsWith(prefix))
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e) => {
    const query = e.target.value
    setSearchQuery(query)
    // Dispatch custom event for search (maintaining compatibility)
    document.dispatchEvent(new CustomEvent('br:search', { detail: query }))
  }

  const rightArea = () => {
    if (isAuthenticated) {
      return (
        <div className="row">
          <span className="muted">{user.name || user.first_name || user.email}</span>
          <Link to={ROUTES.MYPAGE} className="ghost-btn">내 정보</Link>
          <button className="ghost-btn" onClick={logout}>로그아웃</button>
        </div>
      )
    }
    return (
      <div className="row">
        <Link to={ROUTES.LOGIN} className="ghost-btn">로그인</Link>
      </div>
    )
  }

  return (
    <header className="br-header">
      <div className="br-container row">
        <Link to={ROUTES.HOME} className="brand">
          <img src={logo} alt="BingoRoute Logo" className="logo-badge" />
          <span>빙고루트</span>
        </Link>
        {hideSearch ? (
          // 챗봇 화면에서는 검색 입력창 숨김. 레이아웃 간격 유지를 위해 빈 공간 유지
          <div style={{ flex: 1 }} />
        ) : (
          <div className="search">
            <input 
              placeholder="예: 경복궁, 근처 한옥카페…" 
              value={searchQuery}
              onChange={handleSearch}
            />
          </div>
        )}
        {rightArea()}
      </div>
    </header>
  )
}

export default Header
