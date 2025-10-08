// 이름, 이메일, 비밀번호, 비밀번호 확인을 받는 부분과 에러 메시지, 제출 버튼을 포함한 회원가입 폼!!
const SignupForm = ({
  formData,
  error,
  isSubmitting,
  onChange,
  onSubmit,
}) => (
  <form className="form" onSubmit={onSubmit}>
    <input
      type="text"
      name="name" 
      className="input"
      placeholder="이름"
      value={formData.name}
      onChange={onChange}
      required
    />
    <input
      type="email"
      name="email"
      className="input"
      placeholder="이메일"
      value={formData.email}
      onChange={onChange}
      required
    />
    <input
      type="password"
      name="password"
      className="input"
      placeholder="비밀번호"
      value={formData.password}
      onChange={onChange}
      required
    />
    <input
      type="password"
      name="confirmPassword"
      className="input"
      placeholder="비밀번호 확인"
      value={formData.confirmPassword}
      onChange={onChange}
      required
    />
    {error && <div style={{ color: 'red', fontSize: '14px' }}>{error}</div>}
    <button type="submit" className="brand-btn" disabled={isSubmitting}>
      {isSubmitting ? '회원가입 중...' : '회원가입'}
    </button>
  </form>
)

export default SignupForm
