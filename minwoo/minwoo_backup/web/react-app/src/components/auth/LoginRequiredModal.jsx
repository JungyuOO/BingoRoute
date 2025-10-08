import { useNavigate } from 'react-router-dom'
import { useStore } from '../../context/StoreContext'

const LoginRequiredModal = () => {
  const navigate = useNavigate()
  const { loginRequired, setLoginRequired } = useStore()

  if (!loginRequired) return null

  const close = () => setLoginRequired(false)
  const goLogin = () => {
    setLoginRequired(false)
    navigate('/login')
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <div className="header">
          <strong>로그인이 필요합니다</strong>
        </div>
        <div className="content">
          <p className="muted" style={{ marginTop: 0 }}>
            이 기능은 로그인 후 이용할 수 있어요. 로그인하시겠어요?
          </p>
          <div className="row" style={{ justifyContent: 'flex-end', gap: 8 }}>
            <button className="ghost-btn" onClick={close}>나중에</button>
            <button className="brand-btn" onClick={goLogin}>로그인 하기</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginRequiredModal

