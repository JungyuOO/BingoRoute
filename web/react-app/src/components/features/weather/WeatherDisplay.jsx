const WeatherDisplay = ({ currentWeather, selectedDistrict, loading }) => {
  if (loading) {
    return <div className="muted">날씨 정보를 불러오는 중...</div>
  }

  const temperatureValue = currentWeather.temp ?? '정보없음'
  const parsedTemp = parseFloat(temperatureValue)
  const temperatureDisplay = Number.isFinite(parsedTemp)
    ? `${parsedTemp}°C`
    : temperatureValue

  const windDisplay = currentWeather.wind ?? '정보없음'
  const rainfallValue = currentWeather.rainfall ?? '0'
  const rainfallNumber = parseFloat(rainfallValue)
  const rainfallDisplay =
    rainfallValue === '정보없음' ? '정보없음' : `${rainfallValue}mm`
  const showRainfallNote = Number.isFinite(rainfallNumber) && rainfallNumber > 0

  const timeInfo = currentWeather.timeInfo || null

  return (
    <>
      <div className="meta">
        서울 {selectedDistrict} {temperatureDisplay} · 바람 {windDisplay} · 강수 {rainfallDisplay}
      </div>
      <div className="muted" style={{ marginTop: '10px' }}>
        {currentWeather.advice}
      </div>
      {timeInfo && (
        <div className="muted" style={{ marginTop: '10px', fontSize: '1em' }}>
          📅 {timeInfo} | 서울시간 기준
        </div>
      )}
      {showRainfallNote && (
        <div className="muted" style={{ marginTop: '10px' }}>
          강수량: {rainfallDisplay}
        </div>
      )}
    </>
  )
}

export default WeatherDisplay
