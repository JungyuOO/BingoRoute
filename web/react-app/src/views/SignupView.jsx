import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useStore } from '../context/StoreContext'
import { 
  signup as signupRequest, 
  login as loginRequest,
  sendEmailVerification,
  verifyEmailCode
} from '../services/authService'


// '''회원가입창'''

const SignupView = () => {
  const { setSession } = useStore()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    birth_year: '',
    birth_month: '',
    birth_day: '',
    gender: ''
  })
  const [error, setError] = useState('')
  const [emailVerification, setEmailVerification] = useState({
    sent: false,
    verified: false,
    code: '',
    loading: false
  })

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSendVerification = async () => {
    if (!formData.email) {
      setError('이메일을 입력해주세요.')
      return
    }

    setEmailVerification(prev => ({ ...prev, loading: true }))
    setError('')

    try {
      await sendEmailVerification(formData.email)
      setEmailVerification(prev => ({ 
        ...prev, 
        sent: true, 
        loading: false 
      }))
    } catch (err) {
      setError(err.message)
      setEmailVerification(prev => ({ ...prev, loading: false }))
    }
  }

  const handleVerifyCode = async () => {
    if (!emailVerification.code) {
      setError('인증 코드를 입력해주세요.')
      return
    }

    setEmailVerification(prev => ({ ...prev, loading: true }))
    setError('')

    try {
      await verifyEmailCode(formData.email, emailVerification.code)
      setEmailVerification(prev => ({ 
        ...prev, 
        verified: true, 
        loading: false 
      }))
    } catch (err) {
      setError(err.message)
      setEmailVerification(prev => ({ ...prev, loading: false }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!emailVerification.verified) {
      setError('이메일 인증을 완료해주세요.')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.')
      return
    }

    try {
      // 생년월일 조합
      let birth_date = null
      if (formData.birth_year && formData.birth_month && formData.birth_day) {
        birth_date = `${formData.birth_year}-${formData.birth_month.padStart(2, '0')}-${formData.birth_day.padStart(2, '0')}`
      }

      const user = await signupRequest({
        user_id: formData.user_id,
        name: formData.name,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        birth_date: birth_date,
        gender: formData.gender || null
      })
      // Auto-login to obtain access token
      const { access } = await loginRequest({ 
        user_id: formData.user_id, 
        password: formData.password 
      })
      setSession({ ...user, access })
      navigate('/')
    } catch (err) {
      setError(err.message || '회원가입에 실패했습니다.')
    }
  }

  return (
    <div className="br-container">
      <div className="center">
        <div className="panel" style={{ maxWidth: '400px', width: '100%' }}>
          <h2>회원가입</h2>
          <form className="form" onSubmit={handleSubmit}>
            <input
              type="text"
              name="user_id"
              className="input"
              placeholder="사용자 ID"
              value={formData.user_id}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="name"
              className="input"
              placeholder="이름"
              value={formData.name}
              onChange={handleChange}
              required
            />
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="email"
                name="email"
                className="input"
                placeholder="이메일"
                value={formData.email}
                onChange={handleChange}
                required
                style={{ flex: 1 }}
                disabled={emailVerification.verified}
              />
              <button
                type="button"
                onClick={handleSendVerification}
                disabled={emailVerification.loading || emailVerification.verified || !formData.email}
                className={emailVerification.verified ? "ghost-btn" : "neutral-btn"}
                style={{ 
                  whiteSpace: 'nowrap',
                  backgroundColor: emailVerification.verified ? '#5EABA2' : '#FBF5E9',
                  color: emailVerification.verified ? '#FBF5E9' : '#003651',
                  border: '1px solid #5EABA2'
                }}
              >
                {emailVerification.loading ? '발송중...' : 
                 emailVerification.verified ? '인증완료' : 
                 emailVerification.sent ? '재발송' : '인증발송'}
              </button>
            </div>
            {emailVerification.sent && !emailVerification.verified && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="인증 코드 6자리"
                  value={emailVerification.code}
                  onChange={(e) => setEmailVerification(prev => ({ 
                    ...prev, 
                    code: e.target.value 
                  }))}
                  maxLength="6"
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  onClick={handleVerifyCode}
                  disabled={emailVerification.loading || !emailVerification.code}
                  className="neutral-btn"
                  style={{ whiteSpace: 'nowrap' }}
                >
                  {emailVerification.loading ? '확인중...' : '확인하기'}
                </button>
              </div>
            )}
            <input
              type="password"
              name="password"
              className="input"
              placeholder="비밀번호"
              value={formData.password}
              onChange={handleChange}
              required
            />
            <input
              type="password"
              name="confirmPassword"
              className="input"
              placeholder="비밀번호 확인"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '8px' }}>
              <input
                type="number"
                name="birth_year"
                className="input"
                placeholder="년도 (예: 1990)"
                value={formData.birth_year}
                onChange={handleChange}
                min="1900"
                max="2024"
              />
              <input
                type="number"
                name="birth_month"
                className="input"
                placeholder="월 (1-12)"
                value={formData.birth_month}
                onChange={handleChange}
                min="1"
                max="12"
              />
              <input
                type="number"
                name="birth_day"
                className="input"
                placeholder="일 (1-31)"
                value={formData.birth_day}
                onChange={handleChange}
                min="1"
                max="31"
              />
            </div>
            <select
              name="gender"
              className="input"
              value={formData.gender}
              onChange={handleChange}
              style={{ color: formData.gender ? '#003651' : '#999' }}
            >
              <option value="">성별 선택 (선택사항)</option>
              <option value="M">남성</option>
              <option value="F">여성</option>
              <option value="O">기타</option>
            </select>
            {error && <div style={{ color: 'red', fontSize: '14px' }}>{error}</div>}
            <button type="submit" className="brand-btn">회원가입</button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            이미 계정이 있으신가요? <Link to="/login" className="link">로그인</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignupView
