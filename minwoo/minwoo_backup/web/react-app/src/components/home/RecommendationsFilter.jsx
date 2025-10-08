const RecommendationsFilter = ({ areas = [], themes = [], selectedArea, selectedTheme, onAreaChange, onThemeChange }) => {
  return (
    <div className="grid-2" style={{ margin: '10px 0 12px' }}>
      <div>
        <div className="muted" style={{ marginBottom: 6 }}>지역 선택</div>
        <select className="input" value={selectedArea} onChange={(e) => onAreaChange(e.target.value)}>
          <option value="ALL">모든 지역</option>
          {areas.map(a => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>
      <div>
        <div className="muted" style={{ marginBottom: 6 }}>여행 테마</div>
        <select className="input" value={selectedTheme} onChange={(e) => onThemeChange(e.target.value)}>
          <option value="ALL">모든 테마</option>
          {themes.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>
    </div>
  )
}

export default RecommendationsFilter

