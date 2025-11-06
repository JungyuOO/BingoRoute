import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ROUTES } from '../router/routes'
import { findUserId } from '../services/authService'

const FindIdView = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [foundUserId, setFoundUserId] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitted(false)
    setError('')
    setFoundUserId('')
    setLoading(true)

    try {
      const data = await findUserId({ name, email })
      setFoundUserId(data.user_id)
    } catch (err) {
      setError(err.message || '아이디를 찾을 수 없습니다.')
    } finally {
      setLoading(false)
      setSubmitted(true)
    }
  }

  return (
    <div className="br-container">
      <div className="center">
        <div className="panel" style={{ maxWidth: '400px', width: '100%' }}>
          <h2>아이디 찾기</h2>
          <p className="muted" style={{ marginBottom: '16px' }}>
            가입 시 등록한 이름과 이메일을 입력해 주세요.
          </p>
          <form className="form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="input"
              placeholder="이름"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
            <input
              type="email"
              className="input"
              placeholder="이메일"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            <button type="submit" className="brand-btn" disabled={loading}>
              {loading ? '조회 중...' : '아이디 찾기'}
            </button>
          </form>
          {submitted && (
            <div className="muted" style={{ marginTop: '12px', fontSize: '14px' }}>
              {error && <span style={{ color: '#d14343' }}>{error}</span>}
              {!error && foundUserId && (
                <>
                  가입하신 아이디는 <strong>{foundUserId}</strong> 입니다.
                </>
              )}
              {!error && !foundUserId && '입력하신 정보를 다시 확인해주세요.'}
            </div>
          )}
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <Link to={ROUTES.LOGIN} className="link">로그인으로 돌아가기</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FindIdView
