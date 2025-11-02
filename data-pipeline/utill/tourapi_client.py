"""공공데이터 포털 관광 API 호출을 담당하는 경량 클라이언트."""



import ssl, time, requests
from requests.adapters import HTTPAdapter

class TLS12Adapter(HTTPAdapter):
    """TLS 1.2 강제 및 낮은 보안 레벨을 적용하는 어댑터."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        try:
            ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        except Exception:
            pass
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

class TourAPIClient:
    """관광 API 호출과 페이지네이션 처리를 캡슐화한 세션 래퍼."""
    def __init__(self, service_key_decoding: str, base_url: str = "https://apis.data.go.kr/B551011/KorService2",\
        mobile_os: str = "ETC", mobile_app: str = "MyApp", default_type: str = "json",\
            user_agent: str = "tourapi-client/1.0"):
        self.base_url = base_url.rstrip("/")
        self.service_key = service_key_decoding  # 디코딩 키(/ 포함)
        self.common = {
            "serviceKey": self.service_key,
            "MobileOS": mobile_os,
            "MobileApp": mobile_app,
            "_type": default_type,
        }
        self.s = requests.Session()
        self.s.mount("https://", TLS12Adapter())
        self.s.headers["User-Agent"] = user_agent

    def get_once(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        q = {**self.common, **params}
        r = self.s.get(url, params=q, timeout=20)
        r.raise_for_status()
        return r.json()

    # ▼▼ 추가: 응답에서 안전하게 items/totalCount를 꺼내는 유틸 ▼▼
    @staticmethod
    def _extract_items_and_total(resp_json: dict):
        """
        TourAPI 응답에서 items 리스트와 totalCount를 안전하게 뽑는다.
        items가 "", None 등으로 올 때도 빈 리스트로 처리.
        """
        response = resp_json.get("response", {}) if isinstance(resp_json, dict) else {}
        header = response.get("header", {})
        body = response.get("body", {})

        # 에러 헤더가 있을 때도 items는 빈 리스트로 리턴하고 total은 0으로 둔다.
        # (필요하면 여기서 resultCode != "0000"일 때 예외를 던지도록 변경 가능)
        if not isinstance(body, dict):
            return [], 0

        items_field = body.get("items", {})
        items: list
        if isinstance(items_field, dict):
            items = items_field.get("item", []) or []
            if isinstance(items, dict):
                # 어떤 API는 단일 객체로 반환하는 경우가 있어 리스트로 감싼다
                items = [items]
        elif isinstance(items_field, list):
            items = items_field
        else:
            # "", None 등
            items = []

        total = body.get("totalCount")
        try:
            total = int(total) if total is not None else len(items)
        except Exception:
            total = len(items)

        return items, total

    def get_all_pages(self, path: str, params: dict, num_of_rows: int = 100,\
        sleep_sec: float = 0.15, max_pages: int | None = None) -> list[dict]:
        """페이지 단위로 나뉘는 응답을 끝까지 조회해 단일 리스트로 합친다."""
        page_params = {**params, "numOfRows": num_of_rows, "pageNo": 1}
        first = self.get_once(path, page_params)
        items, total = self._extract_items_and_total(first)
        all_items = list(items)

        # 페이지 수 계산
        if total <= num_of_rows:
            return all_items
        pages = (total // num_of_rows) + (1 if (total % num_of_rows) else 0)
        if max_pages is not None:
            pages = min(pages, max_pages)

        for p in range(2, pages + 1):
            page_params["pageNo"] = p
            data = self.get_once(path, page_params)
            page_items, _ = self._extract_items_and_total(data)
            all_items.extend(page_items)
            time.sleep(sleep_sec)

        return all_items
