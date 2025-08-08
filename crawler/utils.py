import os
import re
import json
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class DataValidator:
    """데이터 유효성 검증"""
    
    @staticmethod
    def validate_travel_data(data: Dict) -> bool:
        """여행지 데이터 유효성 검증"""
        required_fields = ['name', 'address']
        
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                return False
        
        return True
    
    @staticmethod
    def clean_address(address: str) -> Dict[str, str]:
        """주소 정리 및 지역 정보 추출"""
        if not address:
            return {'region': '', 'city': '', 'full_address': ''}
        
        # 주소에서 시도, 시군구 추출
        address_parts = address.split()
        region = ''
        city = ''
        
        for part in address_parts:
            if any(suffix in part for suffix in ['시', '도', '특별시', '광역시', '특별자치시']):
                region = part
            elif any(suffix in part for suffix in ['군', '구', '시']):
                city = part
                break
        
        return {
            'region': region,
            'city': city,
            'full_address': address.strip()
        }

class URLGenerator:
    """URL 생성기"""
    
    @staticmethod
    def generate_visitkorea_urls(keyword: str, page_count: int = 5) -> List[str]:
        """한국관광공사 검색 URL 생성"""
        urls = []
        base_url = "https://korean.visitkorea.or.kr/search/searchList.do"
        
        for page in range(1, page_count + 1):
            url = f"{base_url}?keyword={keyword}&page={page}"
            urls.append(url)
        
        return urls
    
    @staticmethod
    def generate_region_based_urls(regions: List[str]) -> Dict[str, List[str]]:
        """지역별 URL 생성"""
        region_urls = {}
        
        for region in regions:
            region_urls[region] = URLGenerator.generate_visitkorea_urls(region)
        
        return region_urls

class DataProcessor:
    """데이터 후처리"""
    
    @staticmethod
    def deduplicate_data(data_list: List[Dict]) -> List[Dict]:
        """중복 데이터 제거"""
        seen = set()
        unique_data = []
        
        for item in data_list:
            # 이름과 주소로 중복 판단
            key = f"{item.get('name', '')}-{item.get('address', '')}"
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        return unique_data
    
    @staticmethod
    def enrich_location_data(data_list: List[Dict]) -> List[Dict]:
        """위치 데이터 보강"""
        validator = DataValidator()
        
        for item in data_list:
            if item.get('address'):
                location_info = validator.clean_address(item['address'])
                item.update(location_info)
        
        return data_list
    
    @staticmethod
    def filter_by_category(data_list: List[Dict], categories: List[str]) -> List[Dict]:
        """카테고리별 필터링"""
        return [item for item in data_list if item.get('category') in categories]

class ReportGenerator:
    """수집 결과 리포트 생성"""
    
    @staticmethod
    def generate_summary_report(data_list: List[Dict]) -> Dict:
        """수집 결과 요약 리포트"""
        if not data_list:
            return {'total': 0, 'categories': {}, 'regions': {}}
        
        total_count = len(data_list)
        
        # 카테고리별 통계
        category_stats = {}
        for item in data_list:
            category = item.get('category', '미분류')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # 지역별 통계
        region_stats = {}
        for item in data_list:
            region = item.get('region', '미지정')
            region_stats[region] = region_stats.get(region, 0) + 1
        
        return {
            'total': total_count,
            'categories': category_stats,
            'regions': region_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def save_report(report: Dict, filename: str = None):
        """리포트 저장"""
        if not filename:
            filename = f"crawling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"리포트 저장: {filepath}")