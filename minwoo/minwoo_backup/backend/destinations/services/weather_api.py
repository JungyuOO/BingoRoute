import datetime
import requests
import pandas as pd
from django.conf import settings

# 🔑 공공데이터포털 서비스 키 (settings에서 관리)
API_KEY = getattr(settings, 'WEATHER_API_KEY', "L+tc+wRhGVm81bYY85f7Y0yOgk52KcfFi/DrgCBIKxq9b3MXSRwzVpMS2jvMrgxI6WmVq1B92LPY4odZw7z9BQ==")

# 서울 구별 격자 좌표
SEOUL_GU = {
    "강남구": (61, 126), "강동구": (62, 126), "강북구": (61, 129), "강서구": (58, 127),
    "관악구": (59, 125), "광진구": (62, 126), "구로구": (58, 125), "금천구": (58, 125),
    "노원구": (61, 129), "도봉구": (61, 130), "동대문구": (61, 127), "동작구": (59, 125),
    "마포구": (59, 127), "서대문구": (59, 127), "서초구": (61, 125), "성동구": (61, 126),
    "성북구": (61, 127), "송파구": (62, 125), "양천구": (58, 126), "영등포구": (58, 126),
    "용산구": (60, 126), "은평구": (59, 127), "종로구": (60, 127), "중구": (60, 126),
    "중랑구": (62, 127)
}


def get_current_weather(nx, ny):
    """현재 관측값 조회"""
    now = datetime.datetime.now()
    
    # 관측 데이터는 매시 40분에 업데이트되므로, 40분 이전이면 이전 시간 사용
    if now.minute < 40:
        now = now - datetime.timedelta(hours=1)
    
    # 만약 전날로 넘어가면 날짜도 조정
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")
    
    print(f"🔍 현재 날씨 요청: base_date={base_date}, base_time={base_time}, nx={nx}, ny={ny} (원래시각: {datetime.datetime.now().strftime('%H:%M')})")

    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "serviceKey": API_KEY, "pageNo": "1", "numOfRows": "1000", "dataType": "JSON",
        "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response_data = response.json()
        print(f"🔍 API 응답 상태: {response.status_code}")
        print(f"🔍 API 응답 데이터: {response_data}")
        
        if 'response' not in response_data:
            print("❌ 응답에 'response' 키가 없습니다")
            return None
            
        if 'body' not in response_data['response']:
            print("❌ 응답에 'body' 키가 없습니다")
            print(f"🔍 response 내용: {response_data['response']}")
            return None
            
        items = response_data['response']['body']['items']['item']
    except Exception as e:
        print(f"❌ 현재 날씨 조회 오류: {e}")
        print(f"🔍 응답 내용: {response.text if 'response' in locals() else 'No response'}")
        return None

    data = {}
    for item in items:
        if item['category'] == 'T1H': data["기온(℃)"] = item['obsrValue']
        if item['category'] == 'REH': data["습도(%)"] = item['obsrValue']
        if item['category'] == 'WSD': data["풍속(m/s)"] = item['obsrValue']
        if item['category'] == 'RN1': data["강수량(mm)"] = item['obsrValue']
    return data


def get_short_forecast(nx, ny):
    """단기예보 조회"""
    now = datetime.datetime.now()
    current_hour = now.hour
    
    available_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    
    # 새벽 0~1시는 전날 23시 발표자료 사용
    if current_hour < 2:
        base_date = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
        hour = 23
    else:
        # 현재 시간보다 이전의 가장 최근 발표 시간 찾기
        valid_hours = [h for h in available_hours if h <= current_hour]
        hour = max(valid_hours) if valid_hours else 23
        base_date = now.strftime("%Y%m%d")
        
        # 만약 valid_hours가 비어있다면 (이론적으로 불가능하지만) 전날 23시 사용
        if not valid_hours:
            base_date = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
            hour = 23
    
    base_time = f"{hour:02d}00"
    print(f"🔍 단기예보 요청: base_date={base_date}, base_time={base_time}, nx={nx}, ny={ny} (현재시각: {current_hour}시)")

    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": API_KEY, "pageNo": "1", "numOfRows": "1000", "dataType": "JSON",
        "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response_data = response.json()
        print(f"🔍 단기예보 API 응답 상태: {response.status_code}")
        
        if 'response' not in response_data:
            print("❌ 단기예보 응답에 'response' 키가 없습니다")
            return []
            
        if 'body' not in response_data['response']:
            print("❌ 단기예보 응답에 'body' 키가 없습니다")
            print(f"🔍 response 내용: {response_data['response']}")
            return []
            
        items = response_data['response']['body']['items']['item']
    except Exception as e:
        print(f"❌ 단기예보 조회 오류: {e}")
        print(f"🔍 응답 내용: {response.text if 'response' in locals() else 'No response'}")
        return []

    forecast = []
    for item in items:
        if item['category'] in ['TMP', 'WSD', 'PCP']:
            forecast.append({
                "예보일자": item['fcstDate'],
                "예보시간": item['fcstTime'],
                "항목": item['category'],
                "값": item['fcstValue']
            })
    return forecast


def get_mid_forecast(region_id="11B10101"):
    """중기예보 조회 (서울 전체)"""
    now = datetime.datetime.now()
    
    # 중기예보는 06시, 18시에 발표됨
    if now.hour < 6:
        # 06시 이전이면 전날 18시 발표자료 사용
        forecast_time = (now - datetime.timedelta(days=1)).strftime("%Y%m%d") + "1800"
    elif now.hour < 18:
        # 18시 이전이면 당일 06시 발표자료 사용
        forecast_time = now.strftime("%Y%m%d") + "0600"
    else:
        # 18시 이후면 당일 18시 발표자료 사용
        forecast_time = now.strftime("%Y%m%d") + "1800"
    
    base_date = forecast_time

    url_land = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
    url_temp = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
    params = {
        "serviceKey": API_KEY, "pageNo": "1", "numOfRows": "10", "dataType": "JSON",
        "regId": region_id, "tmFc": base_date
    }

    try:
        print(f"🔍 중기예보 요청: region_id={region_id}, tmFc={base_date}")
        
        land_response = requests.get(url_land, params=params, timeout=10)
        land_data = land_response.json()
        print(f"🔍 중기예보(육상) API 응답 상태: {land_response.status_code}")
        print(f"🔍 중기예보(육상) API 응답: {land_data}")
        
        if 'response' not in land_data or 'body' not in land_data['response']:
            print("❌ 중기예보(육상) 응답에 'body' 키가 없습니다")
            return []
            
        land_item = land_data['response']['body']['items']['item'][0]
        
        temp_response = requests.get(url_temp, params=params, timeout=10)
        temp_data = temp_response.json()
        print(f"🔍 중기예보(기온) API 응답 상태: {temp_response.status_code}")
        
        if 'response' not in temp_data or 'body' not in temp_data['response']:
            print("❌ 중기예보(기온) 응답에 'body' 키가 없습니다")
            return []
            
        temp_item = temp_data['response']['body']['items']['item'][0]
    except Exception as e:
        print(f"❌ 중기예보 조회 오류: {e}")
        return []

    today = datetime.date.today()
    data = []

    # 3~7일: 오전/오후
    for i in range(3, 8):
        target_date = today + datetime.timedelta(days=i)
        for tp in ["Am", "Pm"]:
            data.append({
                "날짜": target_date.strftime("%Y%m%d"), "시간": tp,
                "항목": "날씨", "값": land_item.get(f"wf{i}{tp}", "-")
            })
            data.append({
                "날짜": target_date.strftime("%Y%m%d"), "시간": tp,
                "항목": "강수확률(%)", "값": land_item.get(f"rnSt{i}{tp}", "-")
            })
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "최저기온(℃)", "값": temp_item.get(f"taMin{i}", "-")
        })
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "최고기온(℃)", "값": temp_item.get(f"taMax{i}", "-")
        })

    # 8~10일: 하루 단위
    for i in range(8, 11):
        target_date = today + datetime.timedelta(days=i)
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "날씨", "값": land_item.get(f"wf{i}", "-")
        })
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "강수확률(%)", "값": land_item.get(f"rnSt{i}", "-")
        })
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "최저기온(℃)", "값": temp_item.get(f"taMin{i}", "-")
        })
        data.append({
            "날짜": target_date.strftime("%Y%m%d"), "시간": "하루",
            "항목": "최고기온(℃)", "값": temp_item.get(f"taMax{i}", "-")
        })

    return data