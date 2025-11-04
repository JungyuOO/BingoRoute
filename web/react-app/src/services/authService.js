const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

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
