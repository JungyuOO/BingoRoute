import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
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

  // ⭐ 여행지 데이터를 저장할 상태, React가 여행 데이터 기억 및 관리할 공간
  const [destinations, setDestinations] = useState([]) // 🍑 여행지API 활성화로 수정 완료

  // 추천 여행지 필터링: 지역/테마
  const [filter, setFilter] = useState('')
  const [selectedArea, setSelectedArea] = useState('ALL')
  const [selectedTheme, setSelectedTheme] = useState('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')

  // 🍑 Django API 연동으로 수정
  // useEffect(() => {
  //   if (DESTINATIONS.length === 0) {
  //     console.warn('⚠️ Django API 미연동 상태 — 여행지 데이터 없음')
  //   }
  // }, [])

  // 🍑 Django API 연동시킬 때 활성화
  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/destinations/')
        const data = await response.json()
  
        if (response.ok) {
          setDestinations(data.results)
        } else {
          console.error('❌ 여행지 데이터 불러오기 실패:', data)
        }
      } catch (error) {
        console.error('⚠️ Django API 요청 오류:', error)
      }
    }
  
    fetchDestinations()
  }, [])
  

  // 유니크 지역/테마 목록 생성
  const areas = Array.from(new Set(destinations.map(d => d.area)))
  const themes = Array.from(new Set(destinations.flatMap(d => d.tags || [])))


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

  const filteredDestinations = destinations.filter(d => {
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