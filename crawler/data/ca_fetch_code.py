# save as: crawler/data/ca_fetch_codes.py (원하는 위치에 저장해도 됨)

import os
import csv
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

# === 설정 ===
API_KEY_RAW = "L+tc+wRhGVm81bYY85f7Y0yOgk52KcfFi/DrgCBIKxq9b3MXSRwzVpMS2jvMrgxI6WmVq1B92LPY4odZw7z9BQ=="
API_KEY = unquote(API_KEY_RAW)  # 인코딩된 키여도 안전하게 디코드해서 사용
BASE_URL = "http://apis.data.go.kr/B551011/KorService2/"
SLEEP = 0.15  # 호출간 딜레이

# 스크립트 기준 상대 경로: crawler/data/ca
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "ca")

DIR_1 = os.path.join(SAVE_ROOT, "1depth")
DIR_2 = os.path.join(SAVE_ROOT, "2depth")
DIR_3 = os.path.join(SAVE_ROOT, "3depth")
DIR_IDX = os.path.join(SAVE_ROOT, "index")


def ensure_dirs():
    for d in [SAVE_ROOT, DIR_1, DIR_2, DIR_3, DIR_IDX]:
        os.makedirs(d, exist_ok=True)


def fetch_xml(endpoint: str, params: dict) -> ET.Element:
    q = {
        "serviceKey": API_KEY,   # 주의: 소문자!
        "MobileOS": "ETC",
        "MobileApp": "MyApp",
        "_type": "xml",
        **params
    }
    r = requests.get(BASE_URL + endpoint, params=q, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {r.url}\n{r.text[:400]}")
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        raise RuntimeError(f"XML ParseError: {e}\n{r.text[:400]}")
    time.sleep(SLEEP)
    return root


def parse_items(root: ET.Element):
    out = []
    for it in root.findall(".//item"):
        code = (it.findtext("code") or "").strip()
        name = (it.findtext("name") or "").strip()
        rnum = (it.findtext("rnum") or "").strip()
        if code:
            out.append((code, name, rnum))
    return out


def fetch_lcls_codes(l1: str | None = None, l2: str | None = None, page_size=200):
    """
    /lclsSystmCode2
      - 1Depth 전체: l1=None, l2=None
      - 2Depth: l1=대분류코드, l2=None
      - 3Depth: l1=대분류코드, l2=중분류코드
    """
    all_rows = []
    page = 1
    while True:
        params = {"numOfRows": page_size, "pageNo": page}
        if l1:
            params["lclsSystm1"] = l1
        if l2:
            params["lclsSystm2"] = l2
        root = fetch_xml("lclsSystmCode2", params)
        items = parse_items(root)
        if not items:
            break
        all_rows.extend(items)
        page += 1
    return all_rows


def write_csv(path: str, header: list[str], rows: list[tuple]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    ensure_dirs()

    # 1) 1Depth
    print("[1Depth] 수집 중…")
    depth1 = fetch_lcls_codes(l1=None, l2=None)
    path_1 = os.path.join(DIR_1, "classification_1depth.csv")
    write_csv(path_1, ["code", "name", "rnum"], depth1)
    print(f"  → {len(depth1)}건 저장: {path_1}")

    # 인덱스 매핑 저장용
    index_2 = []  # (l1_code, l1_name, l2_code, l2_name)
    index_3 = []  # (l1_code, l1_name, l2_code, l2_name, l3_code, l3_name)

    # 2) 각 1Depth에 대한 2Depth
    for l1_code, l1_name, _ in depth1:
        print(f"[2Depth] {l1_code} - {l1_name} 수집 중…")
        depth2 = fetch_lcls_codes(l1=l1_code)

        d2_dir = os.path.join(DIR_2, l1_code)
        d2_path = os.path.join(d2_dir, f"{l1_code}_2depth.csv")
        write_csv(d2_path, ["code", "name", "rnum"], depth2)
        print(f"  → {len(depth2)}건 저장: {d2_path}")

        # 3) 각 2Depth에 대한 3Depth
        for l2_code, l2_name, _ in depth2:
            print(f"    [3Depth] {l1_code}/{l2_code} - {l2_name} 수집 중…")
            depth3 = fetch_lcls_codes(l1=l1_code, l2=l2_code)

            # 인덱스 축적
            for c2 in depth2:
                index_2.append((l1_code, l1_name, c2[0], c2[1]))
            for c3 in depth3:
                index_3.append((l1_code, l1_name, l2_code, l2_name, c3[0], c3[1]))

            d3_dir = os.path.join(DIR_3, l1_code, l2_code)
            d3_path = os.path.join(d3_dir, f"{l1_code}_{l2_code}_3depth.csv")
            write_csv(d3_path, ["code", "name", "rnum"], depth3)
            print(f"      → {len(depth3)}건 저장: {d3_path}")

    # 인덱스 파일 저장
    idx2_path = os.path.join(DIR_IDX, "index_2depth.csv")
    write_csv(idx2_path, ["l1_code", "l1_name", "l2_code", "l2_name"], index_2)
    print(f"\n[INDEX] 1→2 매핑 저장: {idx2_path} ({len(index_2)} rows)")

    idx3_path = os.path.join(DIR_IDX, "index_3depth.csv")
    write_csv(idx3_path, ["l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"], index_3)
    print(f"[INDEX] 1→2→3 매핑 저장: {idx3_path} ({len(index_3)} rows)")

    print("\n✅ 분류체계 1/2/3Depth 수집 및 저장 완료")


if __name__ == "__main__":
    main()
