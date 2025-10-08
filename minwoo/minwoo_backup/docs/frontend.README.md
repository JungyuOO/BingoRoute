# 🎨 BINGOROUTE Frontend (React)

## 📋 프로젝트 개요
- **프레임워크**: React 19.1.1
- **빌드 도구**: Vite 7.1.7
- **라우팅**: React Router DOM 7.9.1
- **스타일링**: CSS (Vanilla)
- **개발 서버**: http://localhost:5173/

## 🚀 React를 선택한 이유

### 1. **컴포넌트 기반 아키텍처**
React의 핵심은 재사용 가능한 컴포넌트입니다. 우리 프로젝트에서 이를 어떻게 활용했는지 살펴보겠습니다.

### 2. **가상 DOM (Virtual DOM)**
React는 가상 DOM을 통해 효율적인 렌더링을 제공합니다.

### 3. **단방향 데이터 플로우**
데이터가 부모에서 자식으로 흐르는 명확한 구조를 제공합니다.

### 4. **풍부한 생태계**
React Router, Context API 등 다양한 라이브러리와 도구를 활용할 수 있습니다.

## 📁 프로젝트 구조

```
web/react-app/
├── public/                     # 정적 파일
│   └── vite.svg               # Vite 로고
├── src/                       # 소스 코드
│   ├── components/            # 재사용 가능한 컴포넌트
│   │   ├── DestinationCard.jsx    # 여행지 카드 컴포넌트
│   │   └── Header.jsx             # 헤더 네비게이션 컴포넌트
│   ├── context/               # React Context
│   │   └── StoreContext.jsx       # 전역 상태 관리
│   ├── data/                  # 정적 데이터
│   │   └── destinations.js        # 여행지 더미 데이터
│   ├── hooks/                 # 커스텀 훅
│   │   └── useAuth.js             # 인증 관련 훅
│   ├── services/              # API 서비스
│   │   └── weatherService.js      # 날씨 API 서비스
│   ├── styles/                # 스타일 파일
│   │   └── global.css             # 전역 CSS 스타일
│   ├── views/                 # 페이지 컴포넌트
│   │   ├── MainView.jsx           # 메인 페이지
│   │   ├── PlaceView.jsx          # 장소 상세 페이지
│   │   ├── PlanView.jsx           # 여행 계획 페이지
│   │   └── MyPageView.jsx         # 마이페이지
│   ├── App.jsx                # 메인 앱 컴포넌트
│   ├── main.jsx               # 앱 진입점
│   └── index.css              # 기본 CSS
├── .gitignore                 # Git 무시 파일
├── eslint.config.js           # ESLint 설정
├── index.html                 # HTML 템플릿
├── package.json               # 의존성 및 스크립트
├── vite.config.js             # Vite 설정
└── README.md                  # 이 파일
```

## 🏗️ React 아키텍처 구현

### 1. **앱 진입점 (Entry Point)**

#### `main.jsx` - React 앱 시작점
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```
- **역할**: React 앱을 DOM에 마운트
- **StrictMode**: 개발 모드에서 잠재적 문제 감지

#### `App.jsx` - 메인 앱 컴포넌트
```jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { StoreProvider } from './context/StoreContext'
import Header from './components/Header'
import MainView from './views/MainView'
import PlaceView from './views/PlaceView'
import PlanView from './views/PlanView'
import MyPageView from './views/MyPageView'
import './styles/global.css'

function App() {
  return (
    <StoreProvider>
      <Router>
        <div className="br-layout">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<MainView />} />
              <Route path="/place/:id" element={<PlaceView />} />
              <Route path="/plan" element={<PlanView />} />
              <Route path="/mypage" element={<MyPageView />} />
            </Routes>
          </main>
        </div>
      </Router>
    </StoreProvider>
  )
}

export default App
```
- **BrowserRouter**: HTML5 History API를 사용한 라우팅
- **StoreProvider**: 전역 상태 관리 Context 제공
- **Routes/Route**: 페이지별 컴포넌트 매핑

### 2. **라우팅 시스템 (React Router)**

우리 프로젝트의 라우팅 구조:
```
/ (루트)           → MainView      (메인 페이지)
/place/:id         → PlaceView     (장소 상세)
/plan              → PlanView      (여행 계획)
/mypage            → MyPageView    (마이페이지)
```

#### 동적 라우팅 예시:
```jsx
// PlaceView에서 URL 파라미터 사용
import { useParams } from 'react-router-dom'

const PlaceView = () => {
  const { id } = useParams() // /place/123 → id = "123"
  // ...
}
```

### 3. **전역 상태 관리 (Context API)**

#### `StoreContext.jsx` - 전역 상태 관리
```jsx
import { createContext, useContext, useState } from 'react'

const StoreContext = createContext()

export const StoreProvider = ({ children }) => {
  const [session, setSession] = useState(null)
  const [wishlist, setWishlist] = useState([])
  const [trips, setTrips] = useState([])

  const value = {
    session, setSession,
    wishlist, setWishlist,
    trips, setTrips
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}

export const useStore = () => {
  const context = useContext(StoreContext)
  if (!context) {
    throw new Error('useStore must be used within StoreProvider')
  }
  return context
}
```
- **createContext**: 전역 상태 컨텍스트 생성
- **Provider**: 하위 컴포넌트에 상태 제공
- **useContext**: 컴포넌트에서 상태 접근

#### 컴포넌트에서 전역 상태 사용:
```jsx
import { useStore } from '../context/StoreContext'

const MyComponent = () => {
  const { session, wishlist, setWishlist } = useStore()
  
  const addToWishlist = (destinationId) => {
    setWishlist([...wishlist, destinationId])
  }
  
  return (
    <div>
      {session ? `안녕하세요, ${session.name}님!` : '로그인해주세요'}
    </div>
  )
}
```

## 🧩 컴포넌트 상세 분석

### 1. **재사용 가능한 컴포넌트 (components/)**

#### `Header.jsx` - 네비게이션 헤더
```jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../context/StoreContext'

const Header = () => {
  const navigate = useNavigate()
  const { session, setSession } = useStore()
  const [searchQuery, setSearchQuery] = useState('')

  // 검색 기능
  const handleSearch = (e) => {
    e.preventDefault()
    // 커스텀 이벤트로 검색어 전달
    document.dispatchEvent(new CustomEvent('br:search', { 
      detail: searchQuery 
    }))
  }

  // 로그인/로그아웃 처리
  const handleAuth = () => {
    if (session) {
      setSession(null) // 로그아웃
    } else {
      // 간단한 로그인 (실제로는 API 호출)
      const userData = { name: '사용자', email: 'user@example.com' }
      setSession(userData)
    }
  }

  return (
    <header className="br-header">
      <div className="br-container">
        <div className="row">
          {/* 로고 */}
          <div className="brand" onClick={() => navigate('/')}>
            <div className="badge">B</div>
            BINGOROUTE
          </div>
          
          {/* 검색 */}
          <form className="search" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="여행지를 검색하세요..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>
          
          {/* 네비게이션 */}
          <nav className="row">
            <button 
              className="ghost-btn" 
              onClick={() => navigate('/plan')}
            >
              여행계획
            </button>
            <button 
              className="ghost-btn" 
              onClick={() => navigate('/mypage')}
            >
              마이페이지
            </button>
            <button className="brand-btn" onClick={handleAuth}>
              {session ? '로그아웃' : '로그인'}
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
```

**React 핵심 개념 적용:**
- **useState**: 검색어 상태 관리
- **useNavigate**: 프로그래밍 방식 페이지 이동
- **useStore**: 전역 상태(로그인 정보) 접근
- **이벤트 처리**: 폼 제출, 클릭 이벤트
- **조건부 렌더링**: 로그인 상태에 따른 버튼 텍스트 변경

#### `DestinationCard.jsx` - 여행지 카드 컴포넌트
```jsx
import { useStore } from '../context/StoreContext'

const DestinationCard = ({ destination }) => {
  const { wishlist, setWishlist } = useStore()
  
  // 찜하기 상태 확인
  const isWishlisted = wishlist.includes(destination.id)
  
  // 찜하기 토글
  const toggleWishlist = (e) => {
    e.stopPropagation() // 카드 클릭 이벤트 방지
    
    if (isWishlisted) {
      setWishlist(wishlist.filter(id => id !== destination.id))
    } else {
      setWishlist([...wishlist, destination.id])
    }
  }

  return (
    <div className="card" onClick={() => navigate(`/place/${destination.id}`)}>
      <div className="img" style={{ 
        backgroundImage: destination.image_url ? `url(${destination.image_url})` : 'none' 
      }}></div>
      
      <div className="body">
        <div className="row">
          <strong>{destination.name}</strong>
          <button 
            className={`wishlist-btn ${isWishlisted ? 'active' : ''}`}
            onClick={toggleWishlist}
          >
            {isWishlisted ? '❤️' : '🤍'}
          </button>
        </div>
        
        <div className="meta">
          {destination.area} · 평점 {destination.rating} · {destination.duration}
        </div>
        
        <p className="muted">{destination.short_description}</p>
        
        {/* 태그 표시 */}
        <div className="tags">
          {destination.tag_names?.map(tag => (
            <span key={tag} className="pill">{tag}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DestinationCard
```

**React 핵심 개념 적용:**
- **Props**: 부모에서 destination 데이터 전달
- **조건부 렌더링**: 찜하기 상태에 따른 하트 아이콘
- **이벤트 버블링 제어**: stopPropagation() 사용
- **배열 렌더링**: map()으로 태그 목록 표시
- **동적 스타일**: 이미지 URL에 따른 배경 이미지

### 2. **페이지 컴포넌트 (views/)**

#### `MainView.jsx` - 메인 페이지
```jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { DESTINATIONS } from '../data/destinations'
import DestinationCard from '../components/DestinationCard'
import { useStore } from '../context/StoreContext'
import { weatherService } from '../services/weatherService'

const MainView = () => {
  const { session } = useStore()
  const navigate = useNavigate()
  
  // 로컬 상태 관리
  const [filter, setFilter] = useState('')
  const [activeTab, setActiveTab] = useState('전체')
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')
  const [weatherData, setWeatherData] = useState({})
  const [loading, setLoading] = useState(true)

  const tabs = ['전체', '인기', '산책', '전통']

  // 날씨 데이터 로드 (컴포넌트 마운트 시)
  useEffect(() => {
    const loadWeatherData = async () => {
      setLoading(true)
      try {
        const currentWeather = await weatherService.getCurrentWeather()
        if (currentWeather) {
          const formattedData = weatherService.formatSeoulWeatherData(currentWeather)
          setWeatherData(formattedData)

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

  // 검색 이벤트 리스너 (Header에서 발생하는 커스텀 이벤트)
  useEffect(() => {
    const handleSearch = (e) => {
      setFilter(e.detail || '')
    }
    document.addEventListener('br:search', handleSearch)
    return () => document.removeEventListener('br:search', handleSearch)
  }, [])

  // 여행 계획 시작
  const handleStartPlanning = () => {
    navigate(session ? '/plan' : '/login')
  }

  // 여행지 필터링 로직
  const filteredDestinations = DESTINATIONS.filter(d => {
    const tabOk = activeTab === '전체' ||
      (activeTab === '인기' ? d.rating >= 4.6 :
        d.tags.some(tag =>
          (activeTab === '산책' && tag === '산책') ||
          (activeTab === '전통' && tag === '전통')
        ))

    const query = filter.trim().toLowerCase()
    const qOk = !query ||
      [d.name, d.area, d.short, d.tags.join(' ')].join(' ').toLowerCase().includes(query)

    return tabOk && qOk
  })

  const currentWeather = weatherData[selectedDistrict] || {
    temp: '정보없음',
    humidity: '정보없음',
    wind: '정보없음',
    sky: '정보없음',
    advice: '날씨 정보를 불러오는 중입니다...'
  }

  return (
    <div className="br-container">
      {/* Hero Section */}
      <div className="hero">
        <div className="pill">서울 추천 가이드</div>
        <h1>서울을 더 스마트하게 여행하세요</h1>
        <p>서울의 흥미로운 로컬 명소를 발견하고, 나만의 여행 루트를 만들어 보세요.</p>
        <button className="brand-btn" onClick={handleStartPlanning}>
          여행 계획 시작하기
        </button>
      </div>

      {/* Weather Section */}
      <div className="section">
        <div className="panel">
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <strong>실시간 날씨 정보</strong>
            {loading ? (
              <span className="muted">로딩 중...</span>
            ) : (
              <select
                className="input"
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
              >
                {Object.keys(weatherData).map(district => (
                  <option key={district} value={district}>{district}</option>
                ))}
              </select>
            )}
          </div>
          
          {loading ? (
            <div className="muted">날씨 정보를 불러오는 중...</div>
          ) : (
            <div className="weather-info">
              <div className="meta">
                서울 {selectedDistrict} 현재 {currentWeather.temp}°C · 
                습도 {currentWeather.humidity}% · 바람 {currentWeather.wind} · 
                하늘 {currentWeather.sky}
              </div>
              <div className="muted">{currentWeather.advice}</div>
            </div>
          )}
        </div>
      </div>

      {/* Destinations Section */}
      <div className="section">
        <h3>추천 여행지</h3>

        {/* Tabs */}
        <div className="tabs">
          {tabs.map(tab => (
            <div
              key={tab}
              className={`tab ${tab === activeTab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </div>
          ))}
        </div>

        {/* Cards Grid */}
        <div className="cards">
          {filteredDestinations.map(destination => (
            <DestinationCard key={destination.id} destination={destination} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MainView
```

**React 핵심 개념 적용:**
- **useState**: 여러 로컬 상태 관리 (필터, 탭, 날씨 데이터 등)
- **useEffect**: 컴포넌트 생명주기 관리 (마운트 시 데이터 로드)
- **비동기 처리**: async/await로 API 호출
- **이벤트 리스너**: 커스텀 이벤트 처리
- **조건부 렌더링**: 로딩 상태, 날씨 데이터 유무에 따른 UI 변경
- **배열 메서드**: filter(), map()으로 데이터 처리
- **컴포넌트 합성**: DestinationCard 컴포넌트 재사용

#### `PlanView.jsx` - 여행 계획 페이지 (핵심 기능)
```jsx
import { useState, useEffect } from 'react'
import { useStore } from '../context/StoreContext'
import { weatherService } from '../services/weatherService'

const PlanView = () => {
  const { session, trips, setTrips } = useStore()
  
  // 단계별 상태 관리
  const [step, setStep] = useState(1)
  const [planData, setPlanData] = useState({
    duration: '',
    style: '',
    budget: '',
    companions: '',
    selectedDate: ''
  })
  
  // 날씨 관련 상태
  const [weatherData, setWeatherData] = useState(null)
  const [weatherRecommendation, setWeatherRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)

  // 로그인 체크
  if (!session) {
    return (
      <div className="br-container">
        <div className="center">
          <p>로그인이 필요합니다.</p>
        </div>
      </div>
    )
  }

  // 다음 단계로 이동 (날씨 데이터 로드 포함)
  const handleNext = async () => {
    if (step === 4) {
      // 4단계에서 5단계로 넘어갈 때 날씨 데이터 로드
      await loadWeatherData()
    }
    if (step < 6) setStep(step + 1)
  }

  // 날씨 데이터 로드 및 추천 계산
  const loadWeatherData = async () => {
    setLoading(true)
    try {
      const midForecast = await weatherService.getMidForecast('서울')
      const formattedData = weatherService.formatMidForecastData(midForecast)
      const recommendation = weatherService.getWeatherRecommendation(formattedData)
      
      setWeatherData(formattedData)
      setWeatherRecommendation(recommendation)
    } catch (error) {
      console.error('날씨 데이터 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  // 여행 계획 저장
  const handleComplete = () => {
    const newTrip = {
      id: Date.now().toString(),
      ...planData,
      date: planData.selectedDate || new Date().toISOString().split('T')[0],
      title: `${planData.duration} 서울 여행`,
      weatherScore: weatherRecommendation?.score || 0
    }
    setTrips([...trips, newTrip])
    alert('여행 계획이 저장되었습니다!')
  }

  // 단계별 렌더링 함수
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div>
            <h3 className="planner-title">여행 기간을 선택해주세요</h3>
            <div className="chips-grid">
              {['당일치기', '1박2일', '2박3일', '3박4일', '일주일'].map(duration => (
                <div
                  key={duration}
                  className={`chip ${planData.duration === duration ? 'active' : ''}`}
                  onClick={() => setPlanData({...planData, duration})}
                >
                  {duration}
                </div>
              ))}
            </div>
          </div>
        )
      
      case 5: // 날씨 기반 추천 단계 (핵심 기능)
        return (
          <div>
            <h3 className="planner-title">날씨 기반 추천</h3>
            <p className="planner-sub">
              향후 10일간의 날씨를 분석해서 최적의 여행 날짜를 추천해드려요
            </p>
            
            {loading ? (
              <div className="center">
                <p>날씨 정보를 불러오는 중...</p>
              </div>
            ) : weatherRecommendation ? (
              <div>
                {/* 날씨 점수 표시 */}
                <div className="weather-score-panel">
                  <div className="score-circle">
                    <span className="score">{weatherRecommendation.score}</span>
                    <span className="score-label">점</span>
                  </div>
                  <p className="score-message">{weatherRecommendation.message}</p>
                </div>

                {/* TOP 3 추천 날짜 */}
                <div className="weather-recommendations">
                  <h4>추천 날짜 TOP 3</h4>
                  <div className="best-days">
                    {weatherRecommendation.bestDays.slice(0, 3).map((day, index) => (
                      <div 
                        key={day.date} 
                        className={`weather-day-card ${
                          planData.selectedDate === day.date ? 'selected' : ''
                        }`}
                        onClick={() => setPlanData({...planData, selectedDate: day.date})}
                      >
                        <div className="day-rank">#{index + 1}</div>
                        <div className="day-date">{day.formattedDate}</div>
                        <div className="day-temp">
                          {day.daily?.minTemp && day.daily?.maxTemp 
                            ? `${day.daily.minTemp}° ~ ${day.daily.maxTemp}°`
                            : '온도 정보 없음'
                          }
                        </div>
                        <div className="day-score">점수: {day.score}</div>
                        <div className="day-rain">
                          강수확률: {Math.round(((day.am?.rainProb || 0) + (day.pm?.rainProb || 0)) / 2)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="center">
                <p>날씨 정보를 불러올 수 없습니다.</p>
              </div>
            )}
          </div>
        )
      
      // 다른 단계들...
      default:
        return null
    }
  }

  return (
    <div className="br-container">
      <div className="section">
        {/* 진행 단계 표시 */}
        <div className="steps">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className={`step ${i <= step ? 'active' : ''}`}></div>
          ))}
        </div>
        
        {renderStep()}

        {/* 네비게이션 버튼 */}
        <div className="planner-actions">
          <button 
            className="neutral-btn" 
            onClick={() => setStep(step - 1)}
            disabled={step === 1}
          >
            이전
          </button>
          
          {step < 6 ? (
            <button 
              className="brand-btn" 
              onClick={handleNext}
              disabled={
                (step === 1 && !planData.duration) ||
                (step === 2 && !planData.style) ||
                (step === 3 && !planData.budget) ||
                (step === 4 && !planData.companions) ||
                (step === 5 && loading)
              }
            >
              {step === 4 ? '날씨 확인하기' : '다음'}
            </button>
          ) : (
            <button className="brand-btn" onClick={handleComplete}>
              계획 저장
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default PlanView
```

**React 핵심 개념 적용:**
- **복잡한 상태 관리**: 여러 단계의 폼 데이터 관리
- **조건부 렌더링**: switch문으로 단계별 UI 렌더링
- **비동기 데이터 처리**: 날씨 API 호출 및 로딩 상태 관리
- **이벤트 핸들링**: 클릭, 폼 제출 등 다양한 이벤트 처리
- **동적 클래스**: 선택된 날짜에 따른 스타일 변경
- **배열 렌더링**: map()으로 추천 날짜 목록 생성
- **전역 상태 업데이트**: 완성된 여행 계획을 전역 상태에 저장

#### `MyPageView.jsx`
- **기능**: 사용자 마이페이지
- **주요 기능**:
  - 사용자 정보 표시
  - 찜한 장소 목록
  - 저장된 여행 계획 목록 (날씨 점수 포함)
  - 날씨 점수별 색상 구분 표시

#### `PlaceView.jsx`
- **기능**: 장소 상세 정보 페이지
- **주요 기능**:
  - 여행지 상세 정보 표시
  - 찜하기 기능
  - 관련 장소 추천

### 🧱 Components (components/)

#### `Header.jsx`
- **기능**: 상단 네비게이션 바
- **주요 기능**:
  - 로고 및 브랜드명
  - 검색 기능
  - 로그인/로그아웃 버튼
  - 페이지 네비게이션

#### `DestinationCard.jsx`
- **기능**: 여행지 카드 컴포넌트
- **주요 기능**:
  - 여행지 이미지, 이름, 평점 표시
  - 태그 표시
  - 찜하기 버튼
  - 클릭 시 상세 페이지 이동

### 3. **서비스 레이어 (services/)**

#### `weatherService.js` - API 통신 및 비즈니스 로직
```jsx
const API_BASE_URL = 'http://localhost:8000'

export const weatherService = {
  // 현재 날씨 정보 조회
  async getCurrentWeather() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/weather/current/`)
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

  // 중기 날씨 예보 조회 (여행 추천용)
  async getMidForecast(region = '서울') {
    try {
      const params = new URLSearchParams()
      params.append('region', region)
      
      const response = await fetch(`${API_BASE_URL}/api/weather/mid-forecast/?${params}`)
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

  // 서울 구별 현재 날씨 데이터 포맷팅
  formatSeoulWeatherData(weatherData) {
    if (!weatherData) return {}

    const seoulDistricts = {}
    
    Object.keys(weatherData).forEach(region => {
      const regionData = weatherData[region]
      
      // 기온, 습도, 풍속, 강수량 데이터 추출
      const temp = regionData['기온(℃)'] || '정보없음'
      const humidity = regionData['습도(%)'] || '정보없음'
      const windSpeed = regionData['풍속(m/s)'] || '정보없음'
      const rainfall = regionData['강수량(mm)'] || '0'
      
      // 날씨 상태 판단 로직
      let sky = '맑음'
      let advice = '좋은 날씨입니다 ☀️'
      
      if (parseFloat(rainfall) > 0) {
        sky = '비'
        advice = '우산을 챙기세요 ☔'
      } else if (parseFloat(humidity) > 80) {
        sky = '흐림'
        advice = '습도가 높아요 💧'
      } else if (parseFloat(windSpeed) > 3) {
        sky = '바람'
        advice = '바람이 강해요 💨'
      }
      
      seoulDistricts[region] = {
        temp: temp,
        humidity: humidity,
        wind: `${windSpeed} m/s`,
        sky: sky,
        advice: advice,
        rainfall: rainfall
      }
    })
    
    return seoulDistricts
  },

  // 중기 예보 데이터 포맷팅
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
      
      // 시간대별 데이터 분류
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

  // 날씨 추천 알고리즘 (핵심 비즈니스 로직)
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

    // 정렬 및 결과 반환
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

  // 점수에 따른 메시지 생성
  getScoreMessage(score) {
    if (score >= 80) return '완벽한 여행 날씨입니다! 🌟'
    if (score >= 70) return '여행하기 좋은 날씨입니다 ☀️'
    if (score >= 60) return '괜찮은 날씨입니다 🌤️'
    if (score >= 50) return '보통 날씨입니다 ⛅'
    if (score >= 40) return '주의가 필요한 날씨입니다 🌧️'
    return '여행을 미루는 것을 고려해보세요 ⛈️'
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
  }
}
```

**React/JavaScript 핵심 개념 적용:**
- **모듈 시스템**: export/import로 서비스 분리
- **비동기 처리**: async/await, Promise 처리
- **에러 핸들링**: try/catch로 API 오류 처리
- **데이터 변환**: 복잡한 API 응답을 UI에 맞게 변환
- **알고리즘 구현**: 날씨 점수 계산 로직
- **유틸리티 함수**: 재사용 가능한 헬퍼 함수들
- **함수형 프로그래밍**: map, filter, reduce 등 배열 메서드 활용

### 4. **커스텀 훅 (hooks/)**

#### `useAuth.js` - 인증 관련 로직
```jsx
import { useState, useEffect } from 'react'

export const useAuth = () => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // 로컬 스토리지에서 사용자 정보 복원
  useEffect(() => {
    const savedUser = localStorage.getItem('bingoroute_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        console.error('사용자 정보 파싱 오류:', error)
        localStorage.removeItem('bingoroute_user')
      }
    }
    setLoading(false)
  }, [])

  // 로그인
  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('bingoroute_user', JSON.stringify(userData))
  }

  // 로그아웃
  const logout = () => {
    setUser(null)
    localStorage.removeItem('bingoroute_user')
  }

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  }
}
```

**React 훅 개념 적용:**
- **커스텀 훅**: 재사용 가능한 상태 로직 분리
- **useEffect**: 컴포넌트 마운트 시 로컬 스토리지 확인
- **useState**: 사용자 상태 및 로딩 상태 관리
- **로컬 스토리지**: 브라우저에 사용자 정보 영속화

### 5. **데이터 레이어 (data/)**

#### `destinations.js` - 정적 데이터
```jsx
export const DESTINATIONS = [
  {
    id: 1,
    name: '경복궁',
    area: '종로구',
    rating: 4.8,
    duration: '2-3시간',
    short_description: '조선왕조의 정궁으로 아름다운 전통 건축을 감상할 수 있습니다.',
    long_description: '1395년에 창건된 조선왕조의 정궁으로...',
    image_url: '/images/gyeongbokgung.jpg',
    tags: ['전통', '역사', '문화'],
    tag_names: ['전통', '역사', '문화']
  },
  {
    id: 2,
    name: '남산타워',
    area: '중구',
    rating: 4.6,
    duration: '1-2시간',
    short_description: '서울의 랜드마크로 시내 전경을 한눈에 볼 수 있습니다.',
    long_description: '1969년에 건립된 서울의 상징적인 타워로...',
    image_url: '/images/namsan-tower.jpg',
    tags: ['관광', '전망'],
    tag_names: ['관광', '전망']
  },
  // ... 더 많은 여행지 데이터
]
```

**데이터 구조 설계:**
- **일관된 스키마**: 모든 여행지가 동일한 필드 구조
- **태그 시스템**: 카테고리별 필터링을 위한 태그 배열
- **평점 시스템**: 인기 여행지 필터링을 위한 수치 데이터
- **이미지 URL**: 동적 이미지 로딩을 위한 경로

### 6. **스타일링 시스템 (styles/)**

#### `global.css` - 전역 스타일 시스템
```css
/* CSS 변수 정의 - 디자인 시스템 */
:root {
  --bg: #0b1b2b;
  --text: #0f172a;
  --muted: #64748b;
  --brand: #2563eb;
  --brand-2: #1d4ed8;
  --card: #ffffff;
  --soft: #f1f5f9;
  --ring: rgba(37,99,235,.35);
}

/* 기본 레이아웃 */
.br-layout {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.br-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 14px 20px;
}

/* 컴포넌트 스타일 */
.card {
  background: var(--card);
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(2,6,23,.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(2,6,23,.12);
}

/* 버튼 시스템 */
.brand-btn {
  background: var(--brand);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  cursor: pointer;
  box-shadow: 0 6px 16px var(--ring);
  transition: all 0.2s;
}

.brand-btn:hover {
  background: var(--brand-2);
  transform: translateY(-1px);
}

.brand-btn:active {
  transform: translateY(1px);
}

/* 날씨 점수 시스템 */
.weather-score-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  margin-bottom: 20px;
}

.score-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  margin-bottom: 12px;
  flex-direction: column;
}

/* 날씨 추천 카드 */
.weather-day-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.weather-day-card:hover {
  border-color: var(--brand);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.weather-day-card.selected {
  border-color: var(--brand);
  background: #eff6ff;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .br-container {
    padding: 12px 16px;
  }
  
  .cards {
    grid-template-columns: 1fr;
  }
  
  .weather-day-card {
    padding: 12px;
  }
}

/* 그리드 시스템 */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.best-days {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
```

**CSS 설계 원칙:**
- **CSS 변수**: 일관된 디자인 시스템
- **BEM 방법론**: 클래스명 규칙 (.br-container, .weather-day-card)
- **컴포넌트 기반**: 재사용 가능한 스타일 블록
- **반응형 디자인**: 모바일 우선 접근법
- **애니메이션**: 부드러운 사용자 경험을 위한 transition
- **그리드 시스템**: CSS Grid를 활용한 유연한 레이아웃

## 🚀 React 핵심 개념 활용

### 1. **컴포넌트 생명주기 관리**
```jsx
// useEffect를 활용한 생명주기 관리
useEffect(() => {
  // 컴포넌트 마운트 시 실행
  const loadData = async () => {
    const data = await weatherService.getCurrentWeather()
    setWeatherData(data)
  }
  
  loadData()
  
  // 클린업 함수 (언마운트 시 실행)
  return () => {
    // 이벤트 리스너 제거, 타이머 정리 등
    document.removeEventListener('br:search', handleSearch)
  }
}, []) // 의존성 배열이 빈 배열이므로 마운트 시에만 실행
```

### 2. **상태 관리 패턴**
```jsx
// 로컬 상태 vs 전역 상태 구분
const MyComponent = () => {
  // 로컬 상태 - 해당 컴포넌트에서만 사용
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  
  // 전역 상태 - 여러 컴포넌트에서 공유
  const { session, wishlist, setWishlist } = useStore()
  
  // 상태 업데이트 함수
  const handleAddToWishlist = (id) => {
    setWishlist(prev => [...prev, id]) // 불변성 유지
  }
}
```

### 3. **이벤트 처리 및 사용자 상호작용**
```jsx
// 다양한 이벤트 처리 패턴
const EventHandlingExample = () => {
  // 폼 제출 처리
  const handleSubmit = (e) => {
    e.preventDefault() // 기본 동작 방지
    // 폼 데이터 처리
  }
  
  // 클릭 이벤트 버블링 제어
  const handleCardClick = (e) => {
    e.stopPropagation() // 이벤트 버블링 방지
    navigate(`/place/${id}`)
  }
  
  // 키보드 이벤트
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input onKeyPress={handleKeyPress} />
      <button onClick={handleCardClick}>클릭</button>
    </form>
  )
}
```

### 4. **조건부 렌더링 패턴**
```jsx
// 다양한 조건부 렌더링 방식
const ConditionalRenderingExample = () => {
  const { session, loading, weatherData } = useStore()
  
  // Early Return 패턴
  if (!session) {
    return <div>로그인이 필요합니다.</div>
  }
  
  return (
    <div>
      {/* 삼항 연산자 */}
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <div>데이터 표시</div>
      )}
      
      {/* 논리 AND 연산자 */}
      {weatherData && (
        <WeatherDisplay data={weatherData} />
      )}
      
      {/* 복잡한 조건부 렌더링 */}
      {weatherData ? (
        weatherData.length > 0 ? (
          <WeatherList data={weatherData} />
        ) : (
          <div>날씨 데이터가 없습니다.</div>
        )
      ) : (
        <div>날씨 정보를 불러오는 중...</div>
      )}
    </div>
  )
}
```

### 5. **리스트 렌더링 및 키 관리**
```jsx
// 효율적인 리스트 렌더링
const ListRenderingExample = () => {
  const [destinations, setDestinations] = useState([])
  
  return (
    <div className="cards">
      {destinations.map(destination => (
        <DestinationCard 
          key={destination.id} // 고유한 키 필수
          destination={destination}
          onWishlistToggle={(id) => handleWishlistToggle(id)}
        />
      ))}
      
      {/* 조건부 리스트 렌더링 */}
      {destinations.length === 0 && (
        <div>여행지가 없습니다.</div>
      )}
    </div>
  )
}
```

### 6. **커스텀 훅 활용**
```jsx
// 재사용 가능한 로직을 커스텀 훅으로 분리
const useWeatherData = (region) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchWeather = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const result = await weatherService.getCurrentWeather(region)
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    if (region) {
      fetchWeather()
    }
  }, [region])
  
  return { data, loading, error }
}

// 컴포넌트에서 커스텀 훅 사용
const WeatherComponent = () => {
  const { data, loading, error } = useWeatherData('서울')
  
  if (loading) return <div>로딩 중...</div>
  if (error) return <div>오류: {error}</div>
  
  return <WeatherDisplay data={data} />
}
```

## 🎯 React 설계 원칙 적용

### 1. **단일 책임 원칙**
- 각 컴포넌트는 하나의 명확한 역할만 담당
- `Header` → 네비게이션, `DestinationCard` → 여행지 표시

### 2. **컴포넌트 합성**
- 작은 컴포넌트들을 조합하여 복잡한 UI 구성
- `MainView` = `Header` + `WeatherSection` + `DestinationGrid`

### 3. **Props를 통한 데이터 전달**
- 부모에서 자식으로 데이터 흐름
- 타입 안정성을 위한 PropTypes 또는 TypeScript 활용 가능

### 4. **상태 끌어올리기 (Lifting State Up)**
- 여러 컴포넌트에서 공유하는 상태는 공통 부모로 이동
- Context API를 통한 전역 상태 관리

### 5. **순수 함수형 컴포넌트**
- 같은 props에 대해 항상 같은 결과 반환
- 사이드 이펙트는 useEffect로 분리

## 📦 의존성

### 주요 라이브러리
```json
{
  "react": "^19.1.1",
  "react-dom": "^19.1.1",
  "react-router-dom": "^7.9.1"
}
```

### 개발 도구
```json
{
  "@vitejs/plugin-react": "^5.0.3",
  "vite": "^7.1.7",
  "eslint": "^9.36.0"
}
```

## 🔧 개발 명령어

```bash
# 개발 서버 시작
npm run dev

# 프로덕션 빌드
npm run build

# 린트 검사
npm run lint

# 프리뷰 서버
npm run preview
```

## 🌐 API 연동

### 백엔드 API 엔드포인트
- **Base URL**: `http://localhost:8000`
- **현재 날씨**: `GET /api/weather/current/`
- **중기 예보**: `GET /api/weather/mid-forecast/`
- **날씨 통계**: `GET /api/weather/statistics/`

### 데이터 플로우
1. **MainView**: 현재 날씨 API → 실시간 날씨 표시
2. **PlanView**: 중기 예보 API → 날씨 분석 → 추천 알고리즘
3. **MyPageView**: 저장된 계획 → 날씨 점수 표시

## 🎯 핵심 알고리즘

### 날씨 추천 점수 계산
```javascript
// 기본 점수: 50점
// 온도 점수: 15-25°C 최적 (+20점)
// 강수확률: 20% 이하 최적 (+20점)
// 최종 점수: 0-100점
```

### 날씨 등급 분류
- **80점 이상**: 완벽한 여행 날씨 🌟
- **70-79점**: 여행하기 좋은 날씨 ☀️
- **60-69점**: 괜찮은 날씨 🌤️
- **50-59점**: 보통 날씨 ⛅
- **50점 미만**: 주의가 필요한 날씨 🌧️

## 🔧 개발 도구 및 설정

### 1. **Vite 설정 (vite.config.js)**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true, // 개발 서버 시작 시 브라우저 자동 열기
    proxy: {
      // API 프록시 설정 (CORS 해결)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // 프로덕션 소스맵 생성
  }
})
```

### 2. **ESLint 설정 (eslint.config.js)**
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    settings: { react: { version: '18.3' } },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]
```

### 3. **패키지 관리 (package.json)**
```json
{
  "name": "react-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.9.1"
  },
  "devDependencies": {
    "@eslint/js": "^9.36.0",
    "@types/react": "^19.1.13",
    "@types/react-dom": "^19.1.9",
    "@vitejs/plugin-react": "^5.0.3",
    "eslint": "^9.36.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.4.0",
    "vite": "^7.1.7"
  }
}
```

## 🚀 성능 최적화 기법

### 1. **React.memo를 활용한 불필요한 리렌더링 방지**
```jsx
import { memo } from 'react'

const DestinationCard = memo(({ destination, onWishlistToggle }) => {
  // 컴포넌트 로직
  return (
    <div className="card">
      {/* 카드 내용 */}
    </div>
  )
})

// props가 변경되지 않으면 리렌더링하지 않음
export default DestinationCard
```

### 2. **useMemo와 useCallback을 활용한 최적화**
```jsx
import { useMemo, useCallback } from 'react'

const MainView = () => {
  const [destinations, setDestinations] = useState([])
  const [filter, setFilter] = useState('')
  
  // 비용이 큰 계산 결과 메모이제이션
  const filteredDestinations = useMemo(() => {
    return destinations.filter(d => 
      d.name.toLowerCase().includes(filter.toLowerCase())
    )
  }, [destinations, filter])
  
  // 함수 메모이제이션 (자식 컴포넌트 props로 전달 시)
  const handleWishlistToggle = useCallback((id) => {
    setWishlist(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    )
  }, [])
  
  return (
    <div>
      {filteredDestinations.map(destination => (
        <DestinationCard 
          key={destination.id}
          destination={destination}
          onWishlistToggle={handleWishlistToggle}
        />
      ))}
    </div>
  )
}
```

### 3. **코드 분할 (Code Splitting)**
```jsx
import { lazy, Suspense } from 'react'

// 동적 import를 통한 코드 분할
const PlanView = lazy(() => import('./views/PlanView'))
const MyPageView = lazy(() => import('./views/MyPageView'))

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainView />} />
        <Route 
          path="/plan" 
          element={
            <Suspense fallback={<div>로딩 중...</div>}>
              <PlanView />
            </Suspense>
          } 
        />
        <Route 
          path="/mypage" 
          element={
            <Suspense fallback={<div>로딩 중...</div>}>
              <MyPageView />
            </Suspense>
          } 
        />
      </Routes>
    </Router>
  )
}
```

## 🧪 테스트 전략

### 1. **컴포넌트 테스트 예시**
```jsx
// DestinationCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react'
import { StoreProvider } from '../context/StoreContext'
import DestinationCard from '../components/DestinationCard'

const mockDestination = {
  id: 1,
  name: '경복궁',
  area: '종로구',
  rating: 4.8,
  tag_names: ['전통', '역사']
}

test('여행지 카드가 올바르게 렌더링된다', () => {
  render(
    <StoreProvider>
      <DestinationCard destination={mockDestination} />
    </StoreProvider>
  )
  
  expect(screen.getByText('경복궁')).toBeInTheDocument()
  expect(screen.getByText('종로구')).toBeInTheDocument()
  expect(screen.getByText('4.8')).toBeInTheDocument()
})

test('찜하기 버튼이 작동한다', () => {
  render(
    <StoreProvider>
      <DestinationCard destination={mockDestination} />
    </StoreProvider>
  )
  
  const wishlistButton = screen.getByRole('button')
  fireEvent.click(wishlistButton)
  
  // 찜하기 상태 변경 확인
  expect(wishlistButton).toHaveTextContent('❤️')
})
```

### 2. **커스텀 훅 테스트**
```jsx
// useAuth.test.js
import { renderHook, act } from '@testing-library/react'
import { useAuth } from '../hooks/useAuth'

test('로그인 기능이 작동한다', () => {
  const { result } = renderHook(() => useAuth())
  
  expect(result.current.user).toBeNull()
  expect(result.current.isAuthenticated).toBe(false)
  
  act(() => {
    result.current.login({ name: '테스트 사용자', email: 'test@example.com' })
  })
  
  expect(result.current.user).toEqual({ name: '테스트 사용자', email: 'test@example.com' })
  expect(result.current.isAuthenticated).toBe(true)
})
```

## 📚 학습 리소스

### React 핵심 개념 학습 순서
1. **JSX와 컴포넌트** → `Header.jsx`, `DestinationCard.jsx` 참고
2. **Props와 State** → `MainView.jsx`의 상태 관리 참고
3. **이벤트 처리** → 클릭, 폼 제출 이벤트 처리 방식
4. **조건부 렌더링** → 로딩 상태, 데이터 유무에 따른 UI 변경
5. **리스트 렌더링** → 여행지 목록, 날씨 데이터 표시
6. **useEffect** → 데이터 로딩, 이벤트 리스너 등록
7. **Context API** → 전역 상태 관리
8. **React Router** → 페이지 라우팅
9. **커스텀 훅** → 재사용 가능한 로직 분리
10. **성능 최적화** → memo, useMemo, useCallback

### 추천 학습 방법
1. 각 컴포넌트 파일을 열어서 실제 구현 코드 분석
2. 개발자 도구에서 React DevTools 사용
3. 코드 수정 후 브라우저에서 실시간 확인
4. 콘솔 로그를 추가하여 데이터 플로우 이해