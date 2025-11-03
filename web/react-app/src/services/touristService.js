const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const TOURIST_SPOTS_ENDPOINT = `${API_BASE}/api/service/tourist_spots/`
const TOURIST_SPOT_DETAIL_ENDPOINT = `${API_BASE}/api/service/tourist_spots/detail/`

const toBoolean = (value) => {
  if (value === null || value === undefined) return false
  const normalized = String(value).trim().toLowerCase()
  return ['y', 'yes', 'true', '1'].includes(normalized)
}

export function normalizeTouristSpot(spot) {
  if (!spot) return null

  const image = spot.firstimage || spot.firstimage2 || null
  const category = spot.category_name ? spot.category_name.trim() : ''
  const rawArea = spot.area || spot.detail_sigungu || spot.detail_address || spot.region || ''
  const area = rawArea ? rawArea.trim() : '지역 정보 없음'

  return {
    id: spot.content_id,
    name: spot.title,
    area,
    rating: spot.rating ?? '정보 없음',
    tags: category ? [category] : [],
    short: category ? `${category} 관련 관광지입니다.` : '상세 설명이 아직 준비되지 않았습니다.',
    image,
    raw: spot,
  }
}

export function normalizeTouristDetail(details) {
  if (!Array.isArray(details) || details.length === 0) {
    return {
      description: '상세 정보가 준비되지 않았습니다.',
      address: '정보 없음',
      tel: '정보 없음',
      restdate: '정보 없음',
      usetime: '정보 없음',
      useseason: '정보 없음',
      facilities: {
        parking: false,
        babyCarriage: false,
        pet: false,
        creditCard: false,
      },
      raw: [],
    }
  }

  const primary = details[0]

  return {
    description: primary.info_text || '상세 정보가 준비되지 않았습니다.',
    address: primary.address || '정보 없음',
    tel: primary.tel || '정보 없음',
    restdate: primary.restdate || '정보 없음',
    usetime: primary.usetime || '정보 없음',
    useseason: primary.useseason || '정보 없음',
    facilities: {
      parking: toBoolean(primary.is_parking),
      babyCarriage: toBoolean(primary.is_baby_carriage),
      pet: toBoolean(primary.is_pet),
      creditCard: toBoolean(primary.is_credit_card),
    },
    raw: details,
  }
}

const parseListResponse = (data) => {
  let records = []
  let next = null
  let previous = null
  let count

  if (Array.isArray(data)) {
    records = data
    count = data.length
  } else if (data && Array.isArray(data.results)) {
    records = data.results
    next = data.next || null
    previous = data.previous || null
    count = typeof data.count === 'number' ? data.count : records.length
  } else if (data && data.data && Array.isArray(data.data)) {
    records = data.data
    next = data.next || null
    previous = data.previous || null
    count = typeof data.count === 'number' ? data.count : records.length
  } else {
    console.warn('알 수 없는 관광지 응답 형식:', data)
    return { items: [], next: null, previous: null, count: 0 }
  }

  return {
    items: records.map(normalizeTouristSpot).filter(Boolean),
    next,
    previous,
    count: count ?? records.length,
  }
}

export async function fetchTouristSpots(params = {}, options = {}) {
  const { directUrl } = options
  const url = directUrl ? new URL(directUrl) : new URL(TOURIST_SPOTS_ENDPOINT)

  if (!directUrl) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, value)
      }
    })
  }

  const res = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(errorText || '관광지 정보를 불러오지 못했습니다.')
  }

  const data = await res.json()
  return parseListResponse(data)
}

export async function fetchTouristSpotDetail(contentId) {
  if (!contentId) throw new Error('contentId가 필요합니다.')
  const res = await fetch(`${TOURIST_SPOT_DETAIL_ENDPOINT}${contentId}/`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })

  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(errorText || '관광지 상세 정보를 불러오지 못했습니다.')
  }

  const data = await res.json()
  let records = []
  if (Array.isArray(data)) {
    records = data
  } else if (Array.isArray(data.results)) {
    records = data.results
  } else if (data.data && Array.isArray(data.data)) {
    records = data.data
  } else {
    console.warn('알 수 없는 관광지 상세 응답 형식:', data)
    return normalizeTouristDetail([])
  }

  return normalizeTouristDetail(records)
}
