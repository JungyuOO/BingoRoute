def main():
    """메인 실행 함수"""
    from basecrawler import TravelDataCrawler
    from utils import URLGenerator
    from utils import DataProcessor
    from utils import ReportGenerator
    import os
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 크롤러 초기화
    crawler = TravelDataCrawler()
    
    # 지역별 크롤링 예시
    regions = ['제주도', '부산', '경주', '전주']
    all_results = []
    
    for region in regions:
        print(f"\n=== {region} 지역 크롤링 시작 ===")
        
        # URL 생성 (실제로는 각 사이트의 URL 패턴에 맞게 수정)
        urls = URLGenerator.generate_visitkorea_urls(region, page_count=3)
        
        # 크롤링 실행
        results = crawler.crawl_urls(urls[:5])  # 테스트용으로 5개만
        all_results.extend(results)
        
        print(f"{region}: {len(results)}개 데이터 수집")
    
    # 데이터 후처리
    processor = DataProcessor()
    
    # 중복 제거
    unique_results = processor.deduplicate_data(all_results)
    print(f"중복 제거 후: {len(unique_results)}개")
    
    # 위치 데이터 보강
    enriched_results = processor.enrich_location_data(unique_results)
    
    # 크롤러에 최종 데이터 설정
    crawler.collected_data = enriched_results
    
    # 결과 저장
    crawler.save_to_csv()
    crawler.save_to_json()
    
    # 리포트 생성
    report_gen = ReportGenerator()
    summary_report = report_gen.generate_summary_report(enriched_results)
    report_gen.save_report(summary_report)
    
    print(f"\n=== 크롤링 완료 ===")
    print(f"총 수집: {len(enriched_results)}개")
    print(f"카테고리별: {summary_report['categories']}")

if __name__ == "__main__":
    main()