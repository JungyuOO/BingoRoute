//폼 입력과 버튼 UI를 전담하는 컴포넌트
const LoginForm = ({
  email,
  password,
  error,
  isSubmitting,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}) => (
  <form className="form" onSubmit={onSubmit}>
    <input
      type="email"
      className="input"
      placeholder="이메일"
      value={email}
      onChange={(event) => onEmailChange(event.target.value)}
      required
    />
    <input
      type="password"
      className="input"
      placeholder="비밀번호"
      value={password}
      onChange={(event) => onPasswordChange(event.target.value)}
      required
    />
    {error && <div style={{ color: 'red', fontSize: '14px' }}>{error}</div>}
    <button type="submit" className="brand-btn" disabled={isSubmitting}>
      {isSubmitting ? '로그인 중...' : '로그인'}
    </button>
  </form>
)

export default LoginForm
