import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin, urlparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('basecrawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """크롤링 베이스 클래스"""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """페이지 가져오기"""
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"페이지 가져오기 실패: {url} - {e}")
            return None
    
    @abstractmethod
    def extract_travel_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """여행지 정보 추출 (각 사이트별로 구현)"""
        pass
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def extract_price(self, text: str) -> Optional[int]:
        """가격 정보 추출"""
        if not text:
            return None
        price_match = re.search(r'[\d,]+', text.replace(',', ''))
        return int(price_match.group()) if price_match else None

class TravelDataModel:
    """여행지 데이터 모델"""
    
    def __init__(self):
        self.data = {
            'name': '',           # 여행지명
            'category': '',       # 카테고리 (액티비티/문화재/자연/지역축제)
            'address': '',        # 주소
            'region': '',         # 지역 (시도)
            'city': '',          # 시군구
            'latitude': None,     # 위도
            'longitude': None,    # 경도
            'description': '',    # 설명
            'price': None,        # 가격
            'operating_hours': '',# 운영시간
            'operating_period': '',# 운영기간
            'contact': '',        # 연락처
            'website': '',        # 웹사이트
            'specialties': [],    # 특산물
            'transportation': {   # 교통 정보
                'public_transport': False,  # 대중교통 가능 여부
                'subway': False,            # 지하철 접근
                'bus': False,              # 버스 접근
                'parking': False           # 주차 가능
            },
            'facilities': [],     # 시설 정보
            'tags': [],          # 태그
            'rating': None,       # 평점
            'reviews_count': 0,   # 리뷰 수
            'source_url': '',     # 출처 URL
            'crawled_at': datetime.now().isoformat()
        }
    
    def to_dict(self) -> Dict:
        return self.data.copy()

class CategoryClassifier:
    """여행지 카테고리 분류기"""
    
    def __init__(self):
        self.category_keywords = {
            '자연': ['산', '바다', '해변', '강', '호수', '폭포', '계곡', '숲', '공원', '자연'],
            '문화재': ['궁', '절', '사찰', '유적', '박물관', '미술관', '문화재', '역사', '전통'],
            '액티비티': ['체험', '놀이', '레포츠', '스키', '수상', '등반', '래프팅', '패러글라이딩'],
            '지역축제': ['축제', '페스티벌', '행사', '이벤트', '마츠리']
        }
    
    def classify(self, name: str, description: str) -> str:
        """카테고리 분류"""
        text = f"{name} {description}".lower()
        
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return '기타'

class TransportationChecker:
    """교통수단 접근성 체크"""
    
    def check_public_transport(self, address: str) -> Dict[str, bool]:
        """대중교통 접근성 확인"""
        transport_info = {
            'public_transport': False,
            'subway': False,
            'bus': False,
            'parking': True  # 기본값
        }
        
        # 키워드 기반 판단
        if any(keyword in address for keyword in ['역', '터미널', '정류장']):
            transport_info['public_transport'] = True
            transport_info['bus'] = True
        
        if '역' in address:
            transport_info['subway'] = True
        
        return transport_info

class TravelDataCrawler:
    """메인 크롤러 클래스"""
    
    def __init__(self):
        self.crawlers = {}  # 각 사이트별 크롤러를 여기에 추가
        self.classifier = CategoryClassifier()
        self.transport_checker = TransportationChecker()
        self.collected_data = []
    
    def add_crawler(self, name: str, crawler: BaseCrawler):
        """새로운 크롤러 추가"""
        self.crawlers[name] = crawler
    
    def crawl_urls(self, urls: List[str], source: str) -> List[Dict]:
        """URL 리스트 크롤링"""
        results = []
        crawler = self.crawlers.get(source)
        
        if not crawler:
            logger.error(f"지원하지 않는 소스: {source}")
            return results
        
        for i, url in enumerate(urls):
            logger.info(f"크롤링 진행: {i+1}/{len(urls)} - {url}")
            
            soup = crawler.get_page(url)
            if soup:
                data = crawler.extract_travel_info(soup, url)
                
                # 카테고리 분류
                data['category'] = self.classifier.classify(
                    data.get('name', ''), 
                    data.get('description', '')
                )
                
                # 교통수단 정보 추가
                if data.get('address'):
                    transport_info = self.transport_checker.check_public_transport(data['address'])
                    data['transportation'].update(transport_info)
                
                results.append(data)
                self.collected_data.append(data)
        
        return results
    
    def save_to_csv(self, filename: str = None):
        """CSV 파일로 저장"""
        if not filename:
            filename = f"travel_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.collected_data:
            logger.warning("저장할 데이터가 없습니다.")
            return
        
        # 중첩된 딕셔너리 평탄화
        flattened_data = []
        for item in self.collected_data:
            flat_item = item.copy()
            
            # transportation 정보 평탄화
            if 'transportation' in flat_item:
                for key, value in flat_item['transportation'].items():
                    flat_item[f'transport_{key}'] = value
                del flat_item['transportation']
            
            # 리스트를 문자열로 변환
            for key, value in flat_item.items():
                if isinstance(value, list):
                    flat_item[key] = ', '.join(map(str, value))
            
            flattened_data.append(flat_item)
        
        df = pd.DataFrame(flattened_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"데이터 저장 완료: {filename}")
    
    def save_to_json(self, filename: str = None):
        """JSON 파일로 저장"""
        if not filename:
            filename = f"travel_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON 저장 완료: {filename}")

# 각 사이트별 크롤러 구현 예시 템플릿
class CustomSiteCrawler(BaseCrawler):
    """사용자 정의 사이트 크롤러 템플릿"""
    
    def __init__(self):
        super().__init__(delay=1.0)
        # 필요한 경우 헤더나 기타 설정 추가
    
    def extract_travel_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """사이트별 데이터 추출 로직 구현"""
        travel_data = TravelDataModel()
        
        try:
            # 여기에 실제 크롤링 로직 구현
            # 예: travel_data.data['name'] = soup.find('h1').get_text()
            travel_data.data['source_url'] = url
            
        except Exception as e:
            logger.error(f"데이터 추출 중 오류: {e}")
        
        return travel_data.to_dict()