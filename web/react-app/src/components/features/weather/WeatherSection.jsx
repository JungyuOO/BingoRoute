import './WeatherSection.css'
import WeatherSelector from './WeatherSelector'
import WeatherDisplay from './WeatherDisplay'

const WeatherSection = ({
  loading,
  districts = [],
  selectedDistrict,
  onChangeDistrict,
  currentWeather,
  meta = null
}) => {
  const isoDate = meta?.forecastDateISO
  const metaText =
    meta?.displayDate && meta?.displayTime
      ? `📅 ${meta.displayDate}${isoDate ? ` (${isoDate})` : ''} ${meta.displayTime} 예보`
      : null

  return (
    <div className="section">
      <div className="panel">
        <div className="row" style={{ justifyContent: 'space-between', marginBottom: '10px' }}>
          <strong>🌏 서울 지역 날씨 정보  </strong>
          <WeatherSelector
            districts={districts}
            selectedDistrict={selectedDistrict}
            onChangeDistrict={onChangeDistrict}
            loading={loading}
          />
        </div>
        {metaText && (
          <div className="muted">
            {metaText}
          </div>
        )}
        <WeatherDisplay
          currentWeather={currentWeather}
          selectedDistrict={selectedDistrict}
          loading={loading}
        />
      </div>
    </div>
  )
}

export default WeatherSection
