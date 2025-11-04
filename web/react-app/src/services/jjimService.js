const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const JJIM_ENDPOINT = `${API_BASE}/api/service/user/jjim/`

export async function fetchJjimList(userId) {
  const url = new URL(JJIM_ENDPOINT)
  url.searchParams.set('user_id', userId)

  const res = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  })

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(errorText || '찜 목록을 불러오지 못했습니다.')
  }

  const data = await res.json()
  return Array.isArray(data.content_id) ? data.content_id : []
}

export async function addJjim(userId, contentId) {
  const res = await fetch(JJIM_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ user_id: userId, content_id: String(contentId) }),
  })

  if (!res.ok) {
    const errorBody = await res.text()
    throw new Error(errorBody || '찜 추가에 실패했습니다.')
  }

  return res.json()
}

export async function removeJjim(userId, contentId) {
  const res = await fetch(JJIM_ENDPOINT, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ user_id: userId, content_id: String(contentId) }),
  })

  if (!res.ok && res.status !== 204) {
    const errorBody = await res.text()
    throw new Error(errorBody || '찜 해제에 실패했습니다.')
  }
}
