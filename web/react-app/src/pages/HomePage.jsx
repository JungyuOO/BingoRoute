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

  // ⭐ 실제 관광지 데이터를 저장할 상태
  const [destinations, setDestinations] = useState([])
  const [loading_destinations, setLoadingDestinations] = useState(true)

  const [filter, setFilter] = useState('')
  // 추천 여행지 필터링: 지역/테마
  const [selectedArea, setSelectedArea] = useState('ALL')
  const [selectedTheme, setSelectedTheme] = useState('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')

  // ⭐ 실제 관광지 API 연동
  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        setLoadingDestinations(true)
        console.log('🔄 관광지 데이터 요청 시작...')
        const response = await fetch('http://localhost:8000/api/service/tourist_spots/')
        const data = await response.json()
        console.log('📊 API 응답:', { status: response.status, dataCount: data.results?.length || 0 })

        if (response.ok && data.results && Array.isArray(data.results)) {
          // tourist_spot 테이블 데이터 사용
          const transformedData = data.results.map(item => ({
            id: item.content_id,
            name: item.title,
            area: item.area_name || item.category_name || '관광지', // tourist_spot_detail에서 가져온 지역 정보
            rating: null, // tourist_spot 테이블에는 평점 정보 없음
            duration: '2-3시간', // 기본값
            tags: item.category_name ? [item.category_name] : ['관광지'],
            short: item.title,
            long: item.title,
            image: item.firstimage || item.firstimage2,
            // 상세 정보
            phone: null,
            closedDays: null,
            operatingHours: null,
            operatingSeason: null,
            parking: null,
            strollerFriendly: null,
            petFriendly: null,
            creditCard: null
          }))
          setDestinations(transformedData)
          console.log('✅ 관광지 데이터 로드 완료:', transformedData.length + '개')
        } else {
          console.error('❌ 관광지 데이터 불러오기 실패:', data)
          setDestinations([])
        }
      } catch (error) {
        console.error('⚠️ 관광지 API 요청 오류:', error)
        setDestinations([])
      } finally {
        setLoadingDestinations(false)
      }
    }

    fetchDestinations()
  }, [])


  // 유니크 지역/테마 목록 생성
  const areas = Array.from(new Set(destinations.map(d => d.area)))
  const themes = Array.from(new Set(destinations.flatMap(d => d.tags)))

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
        {loading_destinations ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>관광지 정보를 불러오는 중...</p>
          </div>
        ) : destinations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>관광지 정보를 불러올 수 없습니다.</p>
          </div>
        ) : (
          <>
            <DestinationsFilter
              areas={areas}
              themes={themes}
              selectedArea={selectedArea}
              selectedTheme={selectedTheme}
              onAreaChange={setSelectedArea}
              onThemeChange={setSelectedTheme}
            />
            <DestinationsGrid items={filteredDestinations} />
          </>
        )}
      </div>
    </div>
  )
}

export default HomePage