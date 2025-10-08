const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function signup({ name, email, password, confirm_password }) {
  const res = await fetch(`${API_BASE}/api/auth/signup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password, confirm_password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || Object.values(data)[0] || '회원가입 실패')
  return data.user
}

export async function login({ email, password }) {
  const res = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '로그인 실패')
  return { user: data.user, access: data.access }
}