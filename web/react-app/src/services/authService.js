const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function extractErrorMessage(data, fallback) {
  if (!data) return fallback
  if (typeof data.detail === 'string') return data.detail

  const nonFieldErrors = data.non_field_errors
  if (Array.isArray(nonFieldErrors) && nonFieldErrors.length > 0) {
    return typeof nonFieldErrors[0] === 'string' ? nonFieldErrors[0] : fallback
  }

  const firstValue = Object.values(data)[0]
  if (Array.isArray(firstValue) && firstValue.length > 0) {
    return typeof firstValue[0] === 'string' ? firstValue[0] : fallback
  }
  if (typeof firstValue === 'string') return firstValue

  return fallback
}

export async function signup({ user_id, name, email, password, confirm_password, birth_date, gender }) {
  const res = await fetch(`${API_BASE}/api/auth/signup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      user_id, 
      name, 
      email, 
      password, 
      confirm_password, 
      birth_date, 
      gender 
    }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || Object.values(data)[0] || '회원가입 실패')
  return data.user
}

export async function login({ user_id, password }) {
  const res = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '로그인 실패')
  return { user: data.user, access: data.access }
}

export async function sendEmailVerification(email) {
  const res = await fetch(`${API_BASE}/api/auth/send-email-verification/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '이메일 발송 실패')
  return data
}

export async function verifyEmailCode(email, code) {
  const res = await fetch(`${API_BASE}/api/auth/verify-email-code/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '인증 실패')
  return data
}

export async function findUserId({ name, email }) {
  const res = await fetch(`${API_BASE}/api/auth/find-id/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(extractErrorMessage(data, '아이디 조회에 실패했습니다.'))
  return data
}

export async function requestPasswordResetCode({ user_id, name, email }) {
  const res = await fetch(`${API_BASE}/api/auth/password-reset/send-code/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, name, email }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(extractErrorMessage(data, '인증 코드 발송에 실패했습니다.'))
  return data
}

export async function verifyPasswordResetCode({ user_id, email, code }) {
  const res = await fetch(`${API_BASE}/api/auth/password-reset/verify-code/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, email, code }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(extractErrorMessage(data, '인증 코드 확인에 실패했습니다.'))
  return data
}

export async function resetPassword({ user_id, email, code, new_password, confirm_password }) {
  const res = await fetch(`${API_BASE}/api/auth/password-reset/confirm/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, email, code, new_password, confirm_password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(extractErrorMessage(data, '비밀번호 재설정에 실패했습니다.'))
  return data
}

export async function validateSession(accessToken) {
  const res = await fetch(`${API_BASE}/api/auth/session/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
  })

  let data = null
  try {
    data = await res.json()
  } catch (error) {
    // Ignore JSON parsing errors for empty responses
  }

  if (!res.ok) {
    const message = data?.detail || '세션 검증에 실패했습니다.'
    const error = new Error(message)
    error.status = res.status
    throw error
  }

  return data
}
