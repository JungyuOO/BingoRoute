// SignupView 컴포넌트 하나로 통합!

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../../context/StoreContext'
import { signup as signupRequest, login as loginRequest } from '../../services/authService'
import SignupForm from './SignupForm' // 회원가입 컴포넌트 불러오기
import SignupPrompt from './SignupPrompt' // 로그인 안내 컴포넌트 불러오기

const SignupView = () => {
  const { setSession } = useStore()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (isSubmitting) return

    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.')
      return
    }

    setIsSubmitting(true)

    try {
      const user = await signupRequest({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
      })

      const { access } = await loginRequest({
        email: formData.email,
        password: formData.password,
      })

      setSession({ ...user, access })
      navigate('/')
    } catch (err) {
      setError(err.message || '회원가입에 실패했습니다.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="br-container">
      <div className="center">
        <div className="panel" style={{ maxWidth: '400px', width: '100%' }}>
          <h2>회원가입</h2>
          <SignupForm
            formData={formData}
            error={error}
            isSubmitting={isSubmitting}
            onChange={handleChange}
            onSubmit={handleSubmit}
          />
          <SignupPrompt />
        </div>
      </div>
    </div>
  )
}

export default SignupView
