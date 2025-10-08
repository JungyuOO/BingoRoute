import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { DESTINATIONS } from '../data/destinations'
import { WeatherSection } from '../components/features/weather'
import { DestinationsFilter, DestinationsGrid } from '../components/features/destinations'
import HeroSection from "../components/features/home/HeroSection";
import { useStore } from '../context/StoreContext'
import { useAuth } from "../hooks/api/useAuth";
import { useWeather } from '../hooks/api/useWeather'

const HomePage = () => {
  const { session } = useStore()
  const { isAuthenticated, promptLogin } = useAuth()
  const { weatherData, loading } = useWeather()
  const navigate = useNavigate()
  const [filter, setFilter] = useState('')
  // 추천 여행지 필터링: 지역/테마
  const [selectedArea, setSelectedArea] = useState('ALL')
  const [selectedTheme, setSelectedTheme] = useState('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')

  // 유니크 지역/테마 목록 생성
  const areas = Array.from(new Set(DESTINATIONS.map(d => d.area)))
  const themes = Array.from(new Set(DESTINATIONS.flatMap(d => d.tags)))

  // 첫 번째 구를 기본 선택
  useEffect(() => {
    const districts = Object.keys(weatherData)
    if (districts.length > 0 && !districts.includes(selectedDistrict)) {
      setSelectedDistrict(districts[0])
    }
  }, [weatherData, selectedDistrict])

  // Listen for search events from header
  useEffect(() => {
    const handleSearch = (e) => {
      setFilter(e.detail || '')
    }
    document.addEventListener('br:search', handleSearch)
    return () => document.removeEventListener('br:search', handleSearch)
  }, [])

  const handleStartPlanning = () => {
    // if (!isAuthenticated) return promptLogin() // ⭐ 삭제 : 비회원 접속 가능하도록 수정
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
        <h2>추천 여행지</h2>
        <DestinationsFilter
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

export default HomePage