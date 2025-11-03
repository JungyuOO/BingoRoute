import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useStore } from '../context/StoreContext'
import { login as loginRequest } from '../services/authService'
import { ROUTES } from '../router/routes'

const LoginView = () => {
  const { setSession } = useStore()
  const navigate = useNavigate()
  const [user_id, setUserId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    try {
      const { user, access } = await loginRequest({ user_id, password })  // const = await (const=def, await=return)
      setSession({ ...user, access })
      navigate(ROUTES.HOME)
    } catch (err) {
      setError(err.message || '로그인에 실패했습니다.')
    }
  }

  return (
    <div className="br-container">
      <div className="center">
        <div className="panel" style={{ maxWidth: '400px', width: '100%' }}>
          <h2>로그인</h2>
          <form className="form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="input"
              placeholder="사용자 ID"
              value={user_id}
              onChange={(event) => setUserId(event.target.value)}
              required
            />
            <input
              type="password"
              className="input"
              placeholder="비밀번호"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
            {error && <div style={{ color: 'red', fontSize: '14px' }}>{error}</div>}
            <button type="submit" className="brand-btn">로그인</button>
          </form>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '14px', fontSize: '15px' }}>
            <Link to={ROUTES.FIND_ID} className="link">아이디 찾기</Link>
            <Link to={ROUTES.FIND_PASSWORD} className="link">비밀번호 찾기</Link>
          </div>
          <div style={{ textAlign: 'center', marginTop: '14px' }}>
            계정이 없으신가요? <Link to={ROUTES.SIGNUP} className="link">회원가입</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginView
