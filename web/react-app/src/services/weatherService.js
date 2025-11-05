const resolveApiBaseUrl = () => {
  // Vite 환경 (import.meta.env.VITE_API_BASE_URL) 우선
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  // CRA 등 process.env 사용 환경
  if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL
  }
  return 'http://localhost:8000'
}

const API_BASE_URL = resolveApiBaseUrl()
const SERVICE_PREFIX = `${API_BASE_URL.replace(/\/$/, '')}/api/service`

const parseNumber = (value) => {
  const num = parseFloat(value)
  return Number.isFinite(num) ? num : null
}

const formatWind = (value) => {
  const num = parseNumber(value)
  if (num === null) return '정보없음'
  return `${num} m/s`
}

const formatRainfall = (value) => {
  if (value === null || value === undefined || value === '') return '0'
  return String(value)
}

const buildAdvice = (temperature, windSpeed, precipitation) => {
  const tempNum = parseNumber(temperature)
  const windNum = parseNumber(windSpeed)
  const rainNum = parseNumber(precipitation)

  if (rainNum !== null && rainNum > 0) {
    return '우산을 챙기세요 ☔'
  }
  if (windNum !== null && windNum >= 5) {
    return '바람이 강해요 💨'
  }
  if (tempNum !== null && tempNum >= 30) {
    return '무더운 날씨입니다 🔥'
  }
  if (tempNum !== null && tempNum <= 0) {
    return '두툼한 옷을 챙기세요 🧣'
  }
  return '여행하기 좋은 날씨입니다 ☀️'
}

export const weatherService = {
  async getCurrentWeather() {
    try {
      const response = await fetch(`${SERVICE_PREFIX}/weather/current/`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || '날씨 데이터를 가져오지 못했습니다.')
      }
      return data.data
    } catch (error) {
      console.error('날씨 API 호출 오류:', error)
      return null
    }
  },

  formatSeoulWeatherData(summary) {
    if (!summary) {
      return {
        meta: null,
        regions: {},
      }
    }

    const forecastDate = summary.forecast_date || null
    const forecastDateISO =
      forecastDate && forecastDate.length === 8
        ? `${forecastDate.slice(0, 4)}-${forecastDate.slice(4, 6)}-${forecastDate.slice(6, 8)}`
        : forecastDate

    const meta = {
      timestamp: summary.timestamp || null,
      forecastDate,
      forecastDateISO,
      forecastTime: summary.forecast_time || null,
      displayDate: summary.display_date || null,
      displayTime: summary.display_time || null,
    }

    const regions = {}

    Object.entries(summary.regions || {}).forEach(([regionName, regionData]) => {
      const temperature = regionData?.temperature ?? '정보없음'
      const windSpeed = regionData?.wind_speed ?? '정보없음'
      const precipitation = regionData?.precipitation ?? '0'

      regions[regionName] = {
        temp: String(temperature),
        wind: formatWind(windSpeed),
        sky: '정보없음',
        rainfall: formatRainfall(precipitation),
        advice: buildAdvice(temperature, windSpeed, precipitation),
        timeInfo: null,
      }
    })

    return { meta, regions }
  },

  formatDate(dateString) {
    if (!dateString || dateString.length !== 8) return dateString

    const year = dateString.substring(0, 4)
    const month = dateString.substring(4, 6)
    const day = dateString.substring(6, 8)

    const date = new Date(year, month - 1, day)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(today.getDate() + 1)

    if (date.toDateString() === today.toDateString()) {
      return '오늘'
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return '내일'
    }
    return `${month}/${day}`
  },

  formatForecastTime(timeString) {
    if (!timeString || timeString.length !== 4) return timeString
    const hour = timeString.substring(0, 2)
    const minute = timeString.substring(2, 4)
    return `${hour}:${minute}`
  },
}
