// 🍑`현재 csv로만 들어가있어서 API 요청해서 받는 걸로 바뀔거라
// 추후 수정 예정
// 기존 api/weather/current ➡️ 현재 api/service/weather 수정

const API_BASE_URL = 'http://localhost:8000'

export const weatherService = {
  // 현재 날씨 정보 조회
  async getCurrentWeather() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/service/weather/`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('날씨 데이터 조회 실패:', data.error)
        return null
      }
    } catch (error) {
      console.error('날씨 API 호출 오류:', error)
      return null
    }
  },

  // 단기 날씨 예보 조회 (3일)
  async getShortForecast(region = null, days = 3) {
    try {
      const params = new URLSearchParams()
      if (region) params.append('region', region)
      params.append('days', days.toString())
      
      const response = await fetch(`${API_BASE_URL}/api/service/weather/forecast/?${params}`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('단기 예보 조회 실패:', data.error)
        return []
      }
    } catch (error) {
      console.error('단기 예보 API 호출 오류:', error)
      return []
    }
  },

  // 중기 날씨 예보 조회 (10일)
  async getMidForecast(region = '서울') {
    try {
      const params = new URLSearchParams()
      params.append('region', region)
      
      const response = await fetch(`${API_BASE_URL}/api/service/weather/mid-forecast/?${params}`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('중기 예보 조회 실패:', data.error)
        return []
      }
    } catch (error) {
      console.error('중기 예보 API 호출 오류:', error)
      return []
    }
  },

  // 날씨 통계 조회
  async getWeatherStatistics() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/service/weather/statistics/`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('날씨 통계 조회 실패:', data.error)
        return null
      }
    } catch (error) {
      console.error('날씨 통계 API 호출 오류:', error)
      return null
    }
  },

  // 특정 시간대의 서울 구별 날씨 조회
  async getWeatherByTime(date = null, time = null) {
    try {
      const params = new URLSearchParams()
      if (date) params.append('date', date)
      if (time) params.append('time', time)
      
      const response = await fetch(`${API_BASE_URL}/api/service/weather/by-time/?${params}`)
      const data = await response.json()
      
      if (data.success) {
        return data.data
      } else {
        console.error('시간대별 날씨 조회 실패:', data.error)
        return []
      }
    } catch (error) {
      console.error('시간대별 날씨 API 호출 오류:', error)
      return []
    }
  },

  // 레거시 - 기존 호환성을 위한 메서드
  async getWeatherForecast(region = null, days = 3) {
    return this.getShortForecast(region, days)
  },

  // 서울 구별 현재 시간대 날씨 데이터를 가공해서 반환
  formatSeoulWeatherData(weatherData) {
    if (!weatherData) return {}

    const seoulDistricts = {}
    
    Object.keys(weatherData).forEach(region => {
      const regionData = weatherData[region]
      
      // 기온, 풍속, 강수량 데이터 추출
      const temp = regionData['기온(℃)'] || '정보없음'
      const windSpeed = regionData['풍속(m/s)'] || '정보없음'
      const rainfall = regionData['강수량(mm)'] || '0'
      const forecastTime = regionData['forecast_time'] || '정보없음'
      const seoulTime = regionData['seoul_time'] || '정보없음'
      
      // 날씨 상태 판단 (간단한 로직)
      let sky = '맑음'
      let advice = '좋은 날씨입니다 ☀️'
      
      if (parseFloat(rainfall) > 0) {
        sky = '비'
        advice = '우산을 챙기세요 ☔'
      } else if (parseFloat(windSpeed) > 3) {
        sky = '바람'
        advice = '바람이 강해요 💨'
      }
      
      // 시간 포맷팅
      const formattedTime = this.formatForecastTime(forecastTime)
      
      seoulDistricts[region] = {
        temp: temp,
        wind: `${windSpeed} m/s`,
        sky: sky,
        advice: advice,
        rainfall: rainfall,
        forecastTime: formattedTime,
        seoulTime: seoulTime,
        timeInfo: `${formattedTime} 예보`
      }
    })
    
    return seoulDistricts
  },

  // 중기 예보 데이터를 가공해서 반환
  formatMidForecastData(midForecastData) {
    if (!midForecastData || !Array.isArray(midForecastData)) return []

    // 날짜별로 그룹화
    const groupedByDate = {}
    
    midForecastData.forEach(item => {
      const date = item.date
      if (!groupedByDate[date]) {
        groupedByDate[date] = {
          date: date,
          region: item.region,
          am: null,
          pm: null,
          daily: null
        }
      }
      
      if (item.period === 'Am') {
        groupedByDate[date].am = {
          weather: item.weather_condition !== 'nan' ? item.weather_condition : '정보없음',
          rainProb: item.rain_probability || 0
        }
      } else if (item.period === 'Pm') {
        groupedByDate[date].pm = {
          weather: item.weather_condition !== 'nan' ? item.weather_condition : '정보없음',
          rainProb: item.rain_probability || 0
        }
      } else if (item.period === '하루') {
        groupedByDate[date].daily = {
          minTemp: item.min_temperature,
          maxTemp: item.max_temperature
        }
      }
    })
    
    // 배열로 변환하고 날짜순 정렬
    return Object.values(groupedByDate)
      .sort((a, b) => a.date.localeCompare(b.date))
      .map(item => ({
        ...item,
        formattedDate: this.formatDate(item.date),
        hasValidData: item.daily && (item.daily.minTemp || item.daily.maxTemp)
      }))
  },

  // 날짜 포맷팅 유틸리티
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
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return '내일'
    } else {
      return `${month}/${day}`
    }
  },

  // 예보 시간 포맷팅 유틸리티
  formatForecastTime(timeString) {
    if (!timeString || timeString.length !== 4) return timeString
    
    const hour = timeString.substring(0, 2)
    const minute = timeString.substring(2, 4)
    
    return `${hour}:${minute}`
  },

  // 시간대별 날씨 데이터 조회 (특정 시간대의 모든 구 데이터)
  async getWeatherByTime(targetDate = null, targetTime = null) {
    try {
      const forecastData = await this.getShortForecast()
      
      if (!targetDate) {
        const today = new Date()
        targetDate = today.getFullYear().toString() + 
                    (today.getMonth() + 1).toString().padStart(2, '0') + 
                    today.getDate().toString().padStart(2, '0')
      }
      
      if (!targetTime) {
        const now = new Date()
        const currentHour = now.getHours()
        // 3시간 간격으로 가장 가까운 시간 찾기
        const forecastHours = [0, 3, 6, 9, 12, 15, 18, 21]
        const closestHour = forecastHours.reduce((prev, curr) => 
          Math.abs(curr - currentHour) < Math.abs(prev - currentHour) ? curr : prev
        )
        targetTime = closestHour.toString().padStart(2, '0') + '00'
      }
      
      // 해당 시간대 데이터 필터링
      const timeData = forecastData.filter(item => 
        item.날짜.toString() === targetDate && 
        item.시간.toString() === targetTime
      )
      
      // 구별로 그룹화
      const weatherByRegion = {}
      timeData.forEach(item => {
        const region = item.지역
        if (!weatherByRegion[region]) {
          weatherByRegion[region] = {
            region: region,
            date: targetDate,
            time: targetTime,
            formattedTime: this.formatForecastTime(targetTime),
            formattedDate: this.formatDate(targetDate)
          }
        }
        
        // 항목별 데이터 매핑
        if (item.항목 === 'TMP') {
          weatherByRegion[region].temperature = item.값
        } else if (item.항목 === 'WSD') {
          weatherByRegion[region].windSpeed = item.값
        } else if (item.항목 === 'PCP') {
          weatherByRegion[region].precipitation = item.값
        }
      })
      
      return Object.values(weatherByRegion)
      
    } catch (error) {
      console.error('시간대별 날씨 조회 오류:', error)
      return []
    }
  },

  // 날씨 추천 로직 (여행 계획용)
  getWeatherRecommendation(midForecastData) {
    if (!midForecastData || midForecastData.length === 0) {
      return {
        score: 0,
        message: '날씨 정보가 없습니다',
        bestDays: [],
        worstDays: []
      }
    }

    const validDays = midForecastData.filter(day => day.hasValidData)
    if (validDays.length === 0) {
      return {
        score: 0,
        message: '유효한 날씨 데이터가 없습니다',
        bestDays: [],
        worstDays: []
      }
    }

    // 각 날짜별 점수 계산
    const scoredDays = validDays.map(day => {
      let score = 50 // 기본 점수
      
      // 온도 점수 (15-25도가 최적)
      if (day.daily.maxTemp) {
        const maxTemp = day.daily.maxTemp
        if (maxTemp >= 15 && maxTemp <= 25) {
          score += 20
        } else if (maxTemp >= 10 && maxTemp <= 30) {
          score += 10
        } else {
          score -= 10
        }
      }
      
      // 강수 확률 점수
      const avgRainProb = ((day.am?.rainProb || 0) + (day.pm?.rainProb || 0)) / 2
      if (avgRainProb <= 20) {
        score += 20
      } else if (avgRainProb <= 40) {
        score += 10
      } else if (avgRainProb <= 60) {
        score -= 10
      } else {
        score -= 20
      }
      
      return { ...day, score }
    })

    // 정렬
    const sortedDays = scoredDays.sort((a, b) => b.score - a.score)
    const avgScore = scoredDays.reduce((sum, day) => sum + day.score, 0) / scoredDays.length

    return {
      score: Math.round(avgScore),
      message: this.getScoreMessage(avgScore),
      bestDays: sortedDays.slice(0, 3),
      worstDays: sortedDays.slice(-2).reverse(),
      allDays: sortedDays
    }
  },

  getScoreMessage(score) {
    if (score >= 80) return '완벽한 여행 날씨입니다! 🌟'
    if (score >= 70) return '여행하기 좋은 날씨입니다 ☀️'
    if (score >= 60) return '괜찮은 날씨입니다 🌤️'
    if (score >= 50) return '보통 날씨입니다 ⛅'
    if (score >= 40) return '주의가 필요한 날씨입니다 🌧️'
    return '여행을 미루는 것을 고려해보세요 ⛈️'
  }
}