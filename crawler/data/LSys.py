import requests
import xml.etree.ElementTree as ET
import os
import time

API_KEY = 'L+tc+wRhGVm81bYY85f7Y0yOgk52KcfFi/DrgCBIKxq9b3MXSRwzVpMS2jvMrgxI6WmVq1B92LPY4odZw7z9BQ=='
BASE_URL = "http://apis.data.go.kr/B551011/KorService2/"

def fetch_xml(endpoint, params):
    params.update({
        "ServiceKey": API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "MyApp",
        "_type": "xml"
    })
    response = requests.get(BASE_URL + endpoint, params=params)
    response.raise_for_status()
    return ET.fromstring(response.text)

def fetch_lcls_systm_codes():
    """분류체계 코드 목록 가져오기 (lclsSystmCode02 사용)"""
    categories = []
    
    try:
        # 1단계: 기본 매개변수로 시도
        root = fetch_xml("lclsSystmCode02", {"numOfRows": 100, "pageNo": 1})
        
        for item in root.findall(".//item"):
            lcls_systm1_cd = item.findtext("lclsSystm1Cd", "")
            lcls_systm1_nm = item.findtext("lclsSystm1Nm", "")
            lcls_systm2_cd = item.findtext("lclsSystm2Cd", "")
            lcls_systm2_nm = item.findtext("lclsSystm2Nm", "")
            lcls_systm3_cd = item.findtext("lclsSystm3Cd", "")
            lcls_systm3_nm = item.findtext("lclsSystm3Nm", "")
            code = item.findtext("code", "")
            name = item.findtext("name", "")
            
            categories.append({
                "lclsSystm1Cd": lcls_systm1_cd,
                "lclsSystm1Nm": lcls_systm1_nm,
                "lclsSystm2Cd": lcls_systm2_cd,
                "lclsSystm2Nm": lcls_systm2_nm,
                "lclsSystm3Cd": lcls_systm3_cd,
                "lclsSystm3Nm": lcls_systm3_nm,
                "code": code,
                "name": name
            })
            
    except Exception as e:
        print(f"lclsSystmCode02 API 호출 실패: {e}")
        print("대안으로 categoryCode2를 사용하여 기본 분류체계를 가져옵니다...")
        
        # 대안: categoryCode2 사용
        try:
            root = fetch_xml("categoryCode2", {"numOfRows": 100, "pageNo": 1})
            for item in root.findall(".//item"):
                code = item.findtext("code", "")
                name = item.findtext("name", "")
                categories.append({
                    "lclsSystm1Cd": code,
                    "lclsSystm1Nm": name,
                    "lclsSystm2Cd": "",
                    "lclsSystm2Nm": "",
                    "lclsSystm3Cd": "",
                    "lclsSystm3Nm": "",
                    "code": code,
                    "name": name
                })
        except Exception as e2:
            print(f"categoryCode2 API도 실패: {e2}")
            # 수동으로 기본 분류체계 추가
            default_categories = [
                {"lclsSystm1Cd": "A01", "lclsSystm1Nm": "자연", "lclsSystm2Cd": "", "lclsSystm2Nm": "", "lclsSystm3Cd": "", "lclsSystm3Nm": "", "code": "A01", "name": "자연"},
                {"lclsSystm1Cd": "A02", "lclsSystm1Nm": "인문(문화/예술/역사)", "lclsSystm2Cd": "", "lclsSystm2Nm": "", "lclsSystm3Cd": "", "lclsSystm3Nm": "", "code": "A02", "name": "인문(문화/예술/역사)"},
                {"lclsSystm1Cd": "A03", "lclsSystm1Nm": "레포츠", "lclsSystm2Cd": "", "lclsSystm2Nm": "", "lclsSystm3Cd": "", "lclsSystm3Nm": "", "code": "A03", "name": "레포츠"},
            ]
            categories = default_categories
            print("기본 분류체계를 사용합니다.")
    
    return categories

def fetch_tour_by_lcls_systm(lcls_systm1_cd="", lcls_systm2_cd="", lcls_systm3_cd=""):
    """분류체계별 관광 정보 조회 (lclsSystm 코드 기준)"""
    all_items = []
    page = 1
    
    while True:
        params = {
            "contentTypeId": "12",  # 관광지
            "numOfRows": 100,
            "pageNo": page
        }
        
        # lclsSystm 매개변수가 지원되지 않을 수 있으므로 cat1으로 대체
        if lcls_systm1_cd:
            params["cat1"] = lcls_systm1_cd
        if lcls_systm2_cd:
            params["cat2"] = lcls_systm2_cd  
        if lcls_systm3_cd:
            params["cat3"] = lcls_systm3_cd
            
        try:
            root = fetch_xml("areaBasedList2", params)
            items = root.findall(".//item")
            
            if not items:
                break
                
            for item in items:
                contentid = item.findtext("contentid", "")
                title = item.findtext("title", "")
                addr = item.findtext("addr1", "")
                areacode = item.findtext("areacode", "")
                creationtime = item.findtext("createdtime", "")
                modifiedtime = item.findtext("modifiedtime", "")
                sigungucode = item.findtext("sigungucode", "")
                cat1 = item.findtext("cat1", "")
                cat2 = item.findtext("cat2", "")
                cat3 = item.findtext("cat3", "")
                mapx = item.findtext("mapx", "")
                mapy = item.findtext("mapy", "")
                tel = item.findtext("tel", "")
                zipcode = item.findtext("zipcode", "")
                
                all_items.append((contentid, title, areacode, addr, creationtime, 
                                modifiedtime, sigungucode, cat1, cat2, 
                                cat3, mapx, mapy, tel, zipcode))
            
            page += 1
            time.sleep(0.2)  # API 호출 속도 제한
            
        except Exception as e:
            print(f"데이터 조회 오류 (lclsSystm1:{lcls_systm1_cd}, lclsSystm2:{lcls_systm2_cd}, lclsSystm3:{lcls_systm3_cd}): {e}")
            break
    
    return all_items

if __name__ == "__main__":
    # 저장 폴더 생성 (crawler 폴더 하위의 crawled_data/분류체계별관광정보/)
    save_dir = os.path.join("..", "crawled_data", "분류체계별관광정보")
    os.makedirs(save_dir, exist_ok=True)

    # 분류체계 코드 가져오기
    print("분류체계 코드 목록 수집 중 (lclsSystmCode02)...")
    categories = fetch_lcls_systm_codes()
    print(f"총 {len(categories)}개 분류체계 발견")

    count_data = []

    for category in categories:
        # 분류체계 이름 생성
        category_name = category["name"]
        if category["lclsSystm1Nm"]:
            category_name = f"{category['lclsSystm1Nm']}_{category_name}"
        if category["lclsSystm2Nm"] and category["lclsSystm2Nm"] != category["lclsSystm1Nm"]:
            category_name = f"{category['lclsSystm1Nm']}_{category['lclsSystm2Nm']}_{category['name']}"
        if category["lclsSystm3Nm"] and category["lclsSystm3Nm"] != category["lclsSystm2Nm"]:
            category_name = f"{category['lclsSystm1Nm']}_{category['lclsSystm2Nm']}_{category['lclsSystm3Nm']}_{category['name']}"
        
        # 파일명에 사용할 수 없는 문자 제거
        safe_name = category_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
        
        print(f"[{category_name}] 관광 정보 수집 중...")
        items = fetch_tour_by_lcls_systm(
            lcls_systm1_cd=category["lclsSystm1Cd"],
            lcls_systm2_cd=category["lclsSystm2Cd"],
            lcls_systm3_cd=category["lclsSystm3Cd"]
        )

        if items:  # 데이터가 있을 때만 파일 생성
            file_path = os.path.join(save_dir, f"{safe_name}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("contentid\ttitle\tareacode\taddr\tcreationtime\tmodifiedtime\tsigungucode\tcat1\tcat2\tcat3\tmapx\tmapy\ttel\tzipcode\n")
                for data in items:
                    f.write("\t".join(data) + "\n")

            count_data.append((category_name, len(items)))
            print(f"  → {len(items)}건 저장 완료")
        else:
            print(f"  → 데이터 없음")

    # 분류체계 정보도 별도 파일로 저장
    category_file_path = os.path.join(save_dir, "_분류체계코드목록.txt")
    with open(category_file_path, "w", encoding="utf-8") as f:
        f.write("lclsSystm1Cd\tlclsSystm1Nm\tlclsSystm2Cd\tlclsSystm2Nm\tlclsSystm3Cd\tlclsSystm3Nm\tcode\tname\n")
        for category in categories:
            f.write(f"{category['lclsSystm1Cd']}\t{category['lclsSystm1Nm']}\t{category['lclsSystm2Cd']}\t{category['lclsSystm2Nm']}\t{category['lclsSystm3Cd']}\t{category['lclsSystm3Nm']}\t{category['code']}\t{category['name']}\n")

    print("\n=== 분류체계별 관광지 개수 ===")
    for name, cnt in count_data:
        print(f"{name}: {cnt}건")

    print(f"\n✅ 총 {len(count_data)}개 분류체계의 관광 정보 저장 완료")
    print(f"✅ 분류체계 코드 목록도 저장 완료 ({len(categories)}개)")