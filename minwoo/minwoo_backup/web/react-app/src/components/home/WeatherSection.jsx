const WeatherSection = ({ loading, districts = [], selectedDistrict, onChangeDistrict, currentWeather }) => {
  return (
    <div className="section">
      <div className="panel">
        <div className="row" style={{ justifyContent: 'space-between', marginBottom: '8px' }}>
          <strong>실시간 날씨 정보</strong>
          {loading ? (
            <span className="muted">로딩 중...</span>
          ) : (
            <select
              className="input"
              value={selectedDistrict}
              onChange={(e) => onChangeDistrict(e.target.value)}
            >
              {districts.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          )}
        </div>
        {loading ? (
          <div className="muted">날씨 정보를 불러오는 중...</div>
        ) : (
          <>
            <div className="meta">
              서울 {selectedDistrict} 현재 {currentWeather.temp}°C · 습도 {currentWeather.humidity}% · 바람 {currentWeather.wind} · 하늘 {currentWeather.sky}
            </div>
            <div className="muted" style={{ marginTop: '6px' }}>
              {currentWeather.advice}
            </div>
            {currentWeather.rainfall && parseFloat(currentWeather.rainfall) > 0 && (
              <div className="muted" style={{ marginTop: '4px' }}>
                강수량: {currentWeather.rainfall}mm
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default WeatherSection

