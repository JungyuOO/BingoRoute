//회원가입 안내 문구와 링크 컴포넌트
import { Link } from 'react-router-dom'

const SignupPrompt = () => (
  <div style={{ textAlign: 'center', marginTop: '16px' }}>
    계정이 없으신가요?{' '}
    <Link to="/signup" className="link">
      회원가입
    </Link>
  </div>
)

export default SignupPrompt
