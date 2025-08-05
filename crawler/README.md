## pip install uv 후 venv 가상환경 접속 후 requirements.txt 파일 순차적으로 실행

## BaseCrawler
    -> 공통 크롤링 로직(페이지 가져오기, 텍스트 정렬 등)
    -> extract_travel_info 는 inherit 클래스에서 구현하도록 강제 지정
## TravelDataModel
    -> 크롤링 결과로 추출한 여행지 데이터의 구조 통일(dict 사용)
## CategoryClassifier / TransportationChecker
    -> 여행지 분류, 교통수단 체크 등 데이터 전처리, 분류, 가공하기 위한 모듈
## TravelDataCrawler
    -> 여러 사이트 크롤러를 (BaseCrawler)를 통해 등록해 URL 별로 크롤링을 진행하여 여행지 정보 데이터를 추출, 가공, 저장 진행하는 메인 
## CustomSiteCrawler
    -> 실제 각 사이트 별 크롤러는 해당 CustomSiteCrawler 클래스를 상속하여 extract_travel_info를 구체적으로 구현해 사용
