// 로그인 안내 문구와 링크만 담당하는 컴포넌트!!
import { Link } from 'react-router-dom'

const SignupPrompt = () => (
  <div style={{ textAlign: 'center', marginTop: '16px' }}>
    이미 계정이 있으신가요?{' '}
    <Link to="/login" className="link">
      로그인
    </Link>
  </div>
)

export default SignupPrompt
