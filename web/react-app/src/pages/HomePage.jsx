import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { WeatherSection } from '../components/features/weather'
import { DestinationsFilter, DestinationsGrid } from '../components/features/destinations'
import HeroSection from "../components/features/home/HeroSection";
import { useWeather } from '../hooks/api/useWeather'
import { fetchTouristSpots } from '../services/touristService'

const HomePage = () => {
  const { weatherData, weatherMeta, loading } = useWeather()
  const navigate = useNavigate()

  const [destinations, setDestinations] = useState([])
  const [destinationsLoading, setDestinationsLoading] = useState(true)
  const [destinationsError, setDestinationsError] = useState(null)
  const [nextPageUrl, setNextPageUrl] = useState(null)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [loadMoreError, setLoadMoreError] = useState(null)


  // 추천 여행지 필터링: 지역/테마
  const [filter, setFilter] = useState('')
  const [selectedArea, setSelectedArea] = useState('ALL')
  const [selectedTheme, setSelectedTheme] = useState('ALL')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')

  const mergeDestinations = useCallback((prev, incoming) => {
    const existingIds = new Set(prev.map(item => String(item.id)))
    const deduped = incoming.filter(item => !existingIds.has(String(item.id)))
    return [...prev, ...deduped]
  }, [])

  useEffect(() => {
    let cancelled = false
    const loadDestinations = async () => {
      setDestinationsLoading(true)
      setDestinationsError(null)
      setLoadMoreError(null)
      try {
        const { items, next } = await fetchTouristSpots()
        if (cancelled) return
        setDestinations(items)
        setNextPageUrl(next)
      } catch (error) {
        if (cancelled) return
        console.error('⚠️ 관광지 데이터를 불러오지 못했습니다:', error)
        setDestinationsError(error.message || '관광지 데이터를 불러오는 중 오류가 발생했습니다.')
      } finally {
        if (!cancelled) {
          setDestinationsLoading(false)
        }
      }
    }

    loadDestinations()
    return () => {
      cancelled = true
    }
  }, [])

  const handleLoadMore = useCallback(async () => {
    if (!nextPageUrl || isLoadingMore) return
    setIsLoadingMore(true)
    try {
      setLoadMoreError(null)
      const { items, next } = await fetchTouristSpots({}, { directUrl: nextPageUrl })
      setDestinations(prev => mergeDestinations(prev, items))
      setNextPageUrl(next)
    } catch (error) {
      console.error('⚠️ 추가 관광지를 불러오지 못했습니다:', error)
      setLoadMoreError(error.message || '추가 관광지를 불러오는 중 오류가 발생했습니다.')
    } finally {
      setIsLoadingMore(false)
    }
  }, [isLoadingMore, mergeDestinations, nextPageUrl])


  // 유니크 지역/테마 목록 생성
  const areas = Array.from(
    new Set(destinations.map(d => d.area).filter(Boolean))
  )
  const themes = Array.from(
    new Set(destinations.flatMap(d => d.tags || []).filter(Boolean))
  )

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
    const themeOk = selectedTheme === 'ALL' || (d.tags || []).includes(selectedTheme)

    const query = filter.trim().toLowerCase()
    const qOk = !query || [
      d.name,
      d.area,
      d.short,
      (d.tags || []).join(' '),
    ].join(' ').toLowerCase().includes(query)

    return areaOk && themeOk && qOk
  })

  const defaultWeather = {
    temp: '정보없음',
    wind: '정보없음',
    sky: '정보없음',
    rainfall: '0',
    advice: '날씨 정보를 불러오는 중입니다...',
  }

  const currentWeather = {
    ...defaultWeather,
    ...(weatherData[selectedDistrict] || {}),
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
        meta={weatherMeta}
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
        {destinationsLoading ? (
          <div className="muted">관광지 데이터를 불러오는 중입니다...</div>
        ) : destinationsError ? (
          <div className="muted" style={{ color: 'red' }}>{destinationsError}</div>
        ) : filteredDestinations.length === 0 ? (
          <div className="muted">조건에 맞는 관광지가 없습니다.</div>
        ) : (
          <>
            <DestinationsGrid items={filteredDestinations} />
            {loadMoreError && (
              <div className="muted" style={{ color: 'red', marginTop: '8px' }}>
                {loadMoreError}
              </div>
            )}
            {nextPageUrl && (
              <div className="center" style={{ marginTop: '16px' }}>
                <button
                  type="button"
                  className="brand-btn"
                  onClick={handleLoadMore}
                  disabled={isLoadingMore}
                >
                  {isLoadingMore ? '불러오는 중...' : '더 보기'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default HomePage
