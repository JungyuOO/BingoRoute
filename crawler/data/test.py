import requests
import xml.etree.ElementTree as ET
import os
import time
API_KEY = '+QHTMndIylEwyljD53lVj/pv1IGuqlsHxl5dO6p7M88rgy1aVsSTnHq9xsi+esYIRugo4YMPa6Gl5Y5aKltAAg=='
BASE_URL = "http://apis.data.go.kr/B551011/KorService2/"
SAVEPATH = ""

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

def fetch_area_codes():
    """광역시·도 코드 목록 가져오기"""
    root = fetch_xml("areaCode2", {"numOfRows": 100, "pageNo": 1})
    return [(item.find("code").text, item.find("name").text) for item in root.findall(".//item")]

def fetch_tour_sync(area_code):
    """관광 정보 동기화 목록 조회 (페이지 전부 수집)"""
    all_items = []
    page = 1
    while True:
        root = fetch_xml("areaBasedSyncList2", {
            "areaCode": area_code,
            "contentTypeId": "12",
            "numOfRows": 100,
            "pageNo": page
        })
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
            all_items.append((contentid, title, areacode, addr, creationtime, modifiedtime, sigungucode, cat1, cat2, cat3, mapx, mapy))
        page += 1
        time.sleep(0.2)  # API 호출 속도 제한 방지
    return all_items

if __name__ == "__main__":
    os.makedirs("C:/Users/Playdata/Desktop/openAPI/관광정보", exist_ok=True)

    provinces = fetch_area_codes()
    print(f"총 {len(provinces)}개 지역 처리 시작")

    count_data = []

    for code, name in provinces:
        print(f"[{name}] 관광 정보 수집 중...")
        items = fetch_tour_sync(code)

        file_path = f"C:/Users/Playdata/Desktop/openAPI/관광정보/{name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"contentid,\ttitle,\tareacode,\taddr,\tcreationtime,\tmodifiedtime,\tsigungucode,\tcat1,\tcat2,\tcat3,\tmapx,\tmapy\n")
            for contentid, title, areacode, addr, creationtime, modifiedtime, sigungucode, cat1, cat2, cat3, mapx, mapy in items:
                f.write(f"{contentid}\t{title}\t{areacode}\t{addr}\t{creationtime}\t{modifiedtime}\t{sigungucode}\t{cat1}\t{cat2}\t{cat3}\t{mapx}\t{mapy}\n")

        count_data.append((name, len(items)))
        print(f"  → {len(items)}건 저장 완료")


    print("\n=== 지역별 관광지 개수 ===")
    for name, cnt in count_data:
        print(f"{name}: {cnt}건")

    print("\n✅ 모든 지역 관광 정보 저장 완료")
