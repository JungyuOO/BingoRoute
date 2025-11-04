const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const TOUR_PLANS_ENDPOINT = `${API_BASE}/api/service/user/tour_plans/`
const TOUR_PLAN_DETAIL_ENDPOINT = (userId, tripId) =>
  `${API_BASE}/api/service/user/tour_plans/${encodeURIComponent(userId)}/trip/${tripId}/`

const TOUR_ITINERARIES_ENDPOINT = `${API_BASE}/api/service/user/tour_itineraries/`
const TOUR_ITINERARY_DETAIL_ENDPOINT = (tripId, seq) =>
  `${API_BASE}/api/service/user/tour_itineraries/trip/${tripId}/seq/${seq}/`

const jsonHeaders = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
}

const handleResponse = async (res, defaultError) => {
  if (res.ok) {
    if (res.status === 204) return null
    try {
      return await res.json()
    } catch (error) {
      return null
    }
  }

  const message = await res.text()
  throw new Error(message || defaultError)
}

export async function fetchTrips(userId) {
  if (!userId) throw new Error('userId is required')
  const url = new URL(TOUR_PLANS_ENDPOINT)
  url.searchParams.set('user_id', userId)

  const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } })
  const data = await handleResponse(res, '여행 계획을 불러오지 못했습니다.')

  if (!data) return []
  if (Array.isArray(data)) return data
  if (Array.isArray(data.results)) return data.results
  if (Array.isArray(data.data)) return data.data
  return []
}

export async function createTrip(userId, payload) {
  if (!userId) throw new Error('userId is required')
  const url = new URL(TOUR_PLANS_ENDPOINT)
  url.searchParams.set('user_id', userId)

  const res = await fetch(url, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload ?? {}),
  })

  return handleResponse(res, '여행 계획 생성에 실패했습니다.')
}

export async function updateTripPlan(userId, tripId, payload) {
  if (!userId) throw new Error('userId is required')
  if (!tripId) throw new Error('tripId is required')

  const res = await fetch(TOUR_PLAN_DETAIL_ENDPOINT(userId, tripId), {
    method: 'PATCH',
    headers: jsonHeaders,
    body: JSON.stringify(payload ?? {}),
  })

  return handleResponse(res, '여행 계획 수정에 실패했습니다.')
}

export async function deleteTrip(userId, tripId) {
  if (!userId) throw new Error('userId is required')
  if (!tripId) throw new Error('tripId is required')

  const res = await fetch(TOUR_PLAN_DETAIL_ENDPOINT(userId, tripId), {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
  })

  if (res.ok || res.status === 404) return null
  const message = await res.text()
  throw new Error(message || '여행 계획 삭제에 실패했습니다.')
}

export async function createItinerary(tripId, payload) {
  if (!tripId) throw new Error('tripId is required')

  const url = new URL(TOUR_ITINERARIES_ENDPOINT)
  url.searchParams.set('trip_id', tripId)

  const res = await fetch(url, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload ?? {}),
  })

  return handleResponse(res, '여행 일정 추가에 실패했습니다.')
}

export async function deleteItinerary(tripId, seq) {
  if (!tripId) throw new Error('tripId is required')
  if (seq === undefined || seq === null) throw new Error('seq is required')

  const res = await fetch(TOUR_ITINERARY_DETAIL_ENDPOINT(tripId, seq), {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
  })

  if (res.ok || res.status === 404) return null
  const message = await res.text()
  throw new Error(message || '여행 일정 삭제에 실패했습니다.')
}
