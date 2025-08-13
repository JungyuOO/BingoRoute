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

def fetch_category_codes():
    """분류체계 코드 목록 가져오기"""
    categories = []
    
    # 대분류 (cat1) 가져오기
    root = fetch_xml("categoryCode2", {"numOfRows": 100, "pageNo": 1})
    for item in root.findall(".//item"):
        code = item.findtext("code", "")
        name = item.findtext("name", "")
        categories.append({
            "cat1": code,
            "cat1_name": name,
            "cat2": "",
            "cat2_name": "",
            "cat3": "",
            "cat3_name": ""
        })
    
    # 중분류 (cat2) 가져오기
    cat2_categories = []
    for cat1_info in categories:
        if cat1_info["cat1"]:
            try:
                root = fetch_xml("categoryCode2", {
                    "cat1": cat1_info["cat1"],
                    "numOfRows": 100,
                    "pageNo": 1
                })
                for item in root.findall(".//item"):
                    code = item.findtext("code", "")
                    name = item.findtext("name", "")
                    if code != cat1_info["cat1"]:  # 대분류와 다른 코드만 추가
                        cat2_categories.append({
                            "cat1": cat1_info["cat1"],
                            "cat1_name": cat1_info["cat1_name"],
                            "cat2": code,
                            "cat2_name": name,
                            "cat3": "",
                            "cat3_name": ""
                        })
                time.sleep(0.1)  # API 호출 속도 제한
            except Exception as e:
                print(f"중분류 조회 오류 ({cat1_info['cat1']}): {e}")
    
    # 소분류 (cat3) 가져오기
    cat3_categories = []
    for cat2_info in cat2_categories:
        if cat2_info["cat2"]:
            try:
                root = fetch_xml("categoryCode2", {
                    "cat1": cat2_info["cat1"],
                    "cat2": cat2_info["cat2"],
                    "numOfRows": 100,
                    "pageNo": 1
                })
                for item in root.findall(".//item"):
                    code = item.findtext("code", "")
                    name = item.findtext("name", "")
                    if code != cat2_info["cat2"]:  # 중분류와 다른 코드만 추가
                        cat3_categories.append({
                            "cat1": cat2_info["cat1"],
                            "cat1_name": cat2_info["cat1_name"],
                            "cat2": cat2_info["cat2"],
                            "cat2_name": cat2_info["cat2_name"],
                            "cat3": code,
                            "cat3_name": name
                        })
                time.sleep(0.1)  # API 호출 속도 제한
            except Exception as e:
                print(f"소분류 조회 오류 ({cat2_info['cat1']}-{cat2_info['cat2']}): {e}")
    
    return categories + cat2_categories + cat3_categories

def fetch_tour_by_category(cat1="", cat2="", cat3=""):
    """분류체계별 관광 정보 조회"""
    all_items = []
    page = 1
    
    while True:
        params = {
            "contentTypeId": "12",  # 관광지
            "numOfRows": 100,
            "pageNo": page
        }
        
        if cat1:
            params["cat1"] = cat1
        if cat2:
            params["cat2"] = cat2
        if cat3:
            params["cat3"] = cat3
            
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
                item_cat1 = item.findtext("cat1", "")
                item_cat2 = item.findtext("cat2", "")
                item_cat3 = item.findtext("cat3", "")
                mapx = item.findtext("mapx", "")
                mapy = item.findtext("mapy", "")
                tel = item.findtext("tel", "")
                zipcode = item.findtext("zipcode", "")
                
                all_items.append((contentid, title, areacode, addr, creationtime, 
                                modifiedtime, sigungucode, item_cat1, item_cat2, 
                                item_cat3, mapx, mapy, tel, zipcode))
            
            page += 1
            time.sleep(0.2)  # API 호출 속도 제한
            
        except Exception as e:
            print(f"데이터 조회 오류 (cat1:{cat1}, cat2:{cat2}, cat3:{cat3}): {e}")
            break
    
    return all_items

if __name__ == "__main__":
    # 저장 폴더 생성 (현재 디렉토리의 data 하위)
    save_dir = os.path.join("data", "분류체계별관광정보")
    os.makedirs(save_dir, exist_ok=True)

    # 분류체계 코드 가져오기
    print("분류체계 코드 목록 수집 중...")
    categories = fetch_category_codes()
    print(f"총 {len(categories)}개 분류체계 발견")

    count_data = []

    for category in categories:
        # 분류체계 이름 생성
        category_name = category["cat1_name"]
        if category["cat2_name"]:
            category_name += f"_{category['cat2_name']}"
        if category["cat3_name"]:
            category_name += f"_{category['cat3_name']}"
        
        # 파일명에 사용할 수 없는 문자 제거
        safe_name = category_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
        
        print(f"[{category_name}] 관광 정보 수집 중...")
        items = fetch_tour_by_category(
            cat1=category["cat1"],
            cat2=category["cat2"] if category["cat2"] else "",
            cat3=category["cat3"] if category["cat3"] else ""
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
        f.write("cat1\tcat1_name\tcat2\tcat2_name\tcat3\tcat3_name\n")
        for category in categories:
            f.write(f"{category['cat1']}\t{category['cat1_name']}\t{category['cat2']}\t{category['cat2_name']}\t{category['cat3']}\t{category['cat3_name']}\n")

    print("\n=== 분류체계별 관광지 개수 ===")
    for name, cnt in count_data:
        print(f"{name}: {cnt}건")

    print(f"\n✅ 총 {len(count_data)}개 분류체계의 관광 정보 저장 완료")
    print(f"✅ 분류체계 코드 목록도 저장 완료 ({len(categories)}개)")