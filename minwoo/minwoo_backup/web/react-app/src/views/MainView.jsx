import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { DESTINATIONS } from '../data/destinations'
import WeatherSection from '../components/home/WeatherSection'
import RecommendationsFilter from '../components/home/RecommendationsFilter'
import DestinationsGrid from '../components/home/DestinationsGrid'
import HeroSection from '../components/home/HeroSection'
import { useStore } from '../context/StoreContext'
import { useAuth } from '../hooks/useAuth'
import { weatherService } from '../services/weatherService'

const MainView = () => {
  const { session } = useStore()
  const { isAuthenticated, promptLogin } = useAuth()
  const navigate = useNavigate()
  const [filter, setFilter] = useState('')
  // 추천 여행지 필터링: 지역/테마
  const [selectedArea, setSelectedArea] = useState('ALL')
  const [selectedTheme, setSelectedTheme] = useState('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')
  const [weatherData, setWeatherData] = useState({})
  const [loading, setLoading] = useState(true)

  // 유니크 지역/테마 목록 생성
  const areas = Array.from(new Set(DESTINATIONS.map(d => d.area)))
  const themes = Array.from(new Set(DESTINATIONS.flatMap(d => d.tags)))

  // 날씨 데이터 로드
  useEffect(() => {
    const loadWeatherData = async () => {
      setLoading(true)
      try {
        const currentWeather = await weatherService.getCurrentWeather()
        if (currentWeather) {
          const formattedData = weatherService.formatSeoulWeatherData(currentWeather)
          setWeatherData(formattedData)

          // 첫 번째 구를 기본 선택
          const districts = Object.keys(formattedData)
          if (districts.length > 0 && !districts.includes(selectedDistrict)) {
            setSelectedDistrict(districts[0])
          }
        }
      } catch (error) {
        console.error('날씨 데이터 로드 실패:', error)
      } finally {
        setLoading(false)
      }
    }

    loadWeatherData()
  }, [])

  // Listen for search events from header
  useEffect(() => {
    const handleSearch = (e) => {
      setFilter(e.detail || '')
    }
    document.addEventListener('br:search', handleSearch)
    return () => document.removeEventListener('br:search', handleSearch)
  }, [])

  const handleStartPlanning = () => {
    if (!isAuthenticated) return promptLogin()
    navigate('/planner')
  }

  const filteredDestinations = DESTINATIONS.filter(d => {
    const areaOk = selectedArea === 'ALL' || d.area === selectedArea
    const themeOk = selectedTheme === 'ALL' || d.tags.includes(selectedTheme)

    const query = filter.trim().toLowerCase()
    const qOk = !query || [d.name, d.area, d.short, d.tags.join(' ')].join(' ').toLowerCase().includes(query)

    return areaOk && themeOk && qOk
  })

  const currentWeather = weatherData[selectedDistrict] || {
    temp: '정보없음',
    humidity: '정보없음',
    wind: '정보없음',
    sky: '정보없음',
    advice: '날씨 정보를 불러오는 중입니다...'
  }

  const districts = Object.keys(weatherData)

  return (
    <div className="br-container">
      <HeroSection onStart={handleStartPlanning} />

      <WeatherSection
        loading={loading}
        districts={districts}
        selectedDistrict={selectedDistrict}
        onChangeDistrict={setSelectedDistrict}
        currentWeather={currentWeather}
      />

      <div className="section">
        <h3>추천 여행지</h3>
        <RecommendationsFilter
          areas={areas}
          themes={themes}
          selectedArea={selectedArea}
          selectedTheme={selectedTheme}
          onAreaChange={setSelectedArea}
          onThemeChange={setSelectedTheme}
        />
        <DestinationsGrid items={filteredDestinations} />
      </div>
    </div>
  )
}

export default MainView
