import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ROUTES } from '../router/routes'
import {
  requestPasswordResetCode,
  verifyPasswordResetCode,
  resetPassword
} from '../services/authService'
import FindpwModal from '../components/common/FindpwModal'

const FindPasswordView = () => {
  const navigate = useNavigate()
  const [userId, setUserId] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [codeSent, setCodeSent] = useState(false)
  const [codeVerified, setCodeVerified] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [sendLoading, setSendLoading] = useState(false)
  const [verifyLoading, setVerifyLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)

  const resetVerificationState = () => {
    setCodeSent(false)
    setCodeVerified(false)
    setCode('')
  }

  const handleBaseFieldChange = (setter) => (event) => {
    setter(event.target.value)
    setError('')
    if (codeSent || codeVerified) {
      resetVerificationState()
    }
  }

  const handleSendCode = async () => {
    if (!userId || !name || !email) {
      setError('아이디, 이름, 이메일을 모두 입력해주세요.')
      return
    }

    setSendLoading(true)
    setError('')

    try {
      await requestPasswordResetCode({ user_id: userId, name, email })
      setCodeSent(true)
      setCodeVerified(false)
      setCode('')
      setError('')
    } catch (err) {
      setError(err.message || '인증 코드 발송에 실패했습니다.')
    } finally {
      setSendLoading(false)
    }
  }

  const handleVerifyCode = async () => {
    if (!code) {
      setError('인증 코드를 입력해주세요.')
      return
    }

    setVerifyLoading(true)
    setError('')

    try {
      await verifyPasswordResetCode({ user_id: userId, email, code })
      setCodeVerified(true)
      setError('')
    } catch (err) {
      setError(err.message || '인증 코드 확인에 실패했습니다.')
    } finally {
      setVerifyLoading(false)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!codeVerified) {
      setError('인증 코드를 확인한 후 비밀번호를 재설정할 수 있습니다.')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('새 비밀번호가 일치하지 않습니다.')
      return
    }

    setSubmitLoading(true)
    try {
      await resetPassword({
        user_id: userId,
        email,
        code,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      setNewPassword('')
      setConfirmPassword('')
      resetVerificationState()
      setShowSuccessModal(true)
    } catch (err) {
      setError(err.message || '비밀번호 재설정에 실패했습니다.')
    } finally {
      setSubmitLoading(false)
    }
  }

  const sendButtonLabel = sendLoading
    ? '발송중...'
    : codeVerified
      ? '인증완료'
      : codeSent
        ? '재발송'
        : '인증코드 발송'

  const verifyButtonLabel = verifyLoading
    ? '확인중...'
    : codeVerified
      ? '확인완료'
      : '확인하기'

  return (
    <div className="br-container">
      <div className="center">
        <div className="panel" style={{ maxWidth: '400px', width: '100%' }}>
          <h2>비밀번호 찾기</h2>
          <p className="muted" style={{ marginBottom: '16px' }}>
            가입한 아이디, 이름, 이메일을 입력하고 인증 코드를 받아 새 비밀번호를 설정하세요.
          </p>
          <form className="form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="input"
              placeholder="아이디"
              value={userId}
              onChange={handleBaseFieldChange(setUserId)}
              required
            />
            <input
              type="text"
              className="input"
              placeholder="이름"
              value={name}
              onChange={handleBaseFieldChange(setName)}
              required
            />
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="email"
                className="input"
                placeholder="이메일"
                value={email}
                onChange={handleBaseFieldChange(setEmail)}
                required
                disabled={codeVerified}
                style={{ flex: 1 }}
              />
              <button
                type="button"
                onClick={handleSendCode}
                disabled={sendLoading || codeVerified}
                className={codeVerified ? 'ghost-btn' : 'neutral-btn'}
                style={{
                  whiteSpace: 'nowrap',
                  backgroundColor: codeVerified ? '#5EABA2' : '#FBF5E9',
                  color: codeVerified ? '#FBF5E9' : '#003651',
                  border: '1px solid #5EABA2'
                }}
              >
                {sendButtonLabel}
              </button>
            </div>

            {codeSent && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="인증 코드 6자리"
                  value={code}
                  onChange={(event) => {
                    setCode(event.target.value)
                    setError('')
                  }}
                  maxLength={6}
                  disabled={codeVerified}
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  onClick={handleVerifyCode}
                  disabled={verifyLoading || codeVerified || !code}
                  className={codeVerified ? 'ghost-btn' : 'neutral-btn'}
                  style={{
                    whiteSpace: 'nowrap',
                    backgroundColor: codeVerified ? '#5EABA2' : '#FBF5E9',
                    color: codeVerified ? '#FBF5E9' : '#003651',
                    border: '1px solid #5EABA2'
                  }}
                >
                  {verifyButtonLabel}
                </button>
              </div>
            )}

            {codeVerified && (
              <>
                <input
                  type="password"
                  className="input"
                  placeholder="새 비밀번호"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  required
                />
                <input
                  type="password"
                  className="input"
                  placeholder="새 비밀번호 확인"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  required
                />
              </>
            )}

            {error && (
              <div style={{ color: '#d14343', fontSize: '14px' }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="brand-btn"
              disabled={submitLoading || !codeVerified}
            >
              {submitLoading ? '재설정 중...' : '비밀번호 재설정'}
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <Link to={ROUTES.LOGIN} className="link">로그인으로 돌아가기</Link>
          </div>
        </div>
      </div>
      <FindpwModal
        open={showSuccessModal}
        title="비밀번호 재설정 완료"
        description="새로운 비밀번호로 다시 로그인해 주세요."
        onClose={() => {
          setShowSuccessModal(false)
          navigate(ROUTES.LOGIN)
        }}
        actions={[
          {
            label: '확인',
            variant: 'brand',
            onClick: () => {
              setShowSuccessModal(false)
              navigate(ROUTES.LOGIN)
            }
          }
        ]}
      />
    </div>
  )
}

export default FindPasswordView
