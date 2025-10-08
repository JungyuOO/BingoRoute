const HeroSection = ({ onStart }) => {
  return (
    <div className="hero">
      <div className="pill" style={{ display: 'inline-block', marginBottom: '8px' }}>
        서울 추천 가이드
      </div>
      <h1>서울을 더 스마트하게 여행하세요</h1>
      <p>서울의 흥미로운 로컬 명소를 발견하고, 나만의 여행 루트를 만들어 보세요.</p>
      <div style={{ marginTop: '10px' }}>
        <button className="brand-btn" onClick={onStart}>
          여행 계획 시작하기
        </button>
      </div>
    </div>
  )
}

export default HeroSection

