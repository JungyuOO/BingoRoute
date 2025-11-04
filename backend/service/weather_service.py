import csv
import datetime
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from django.conf import settings

from .weather_client import SEOUL_GU

try:  # Python 3.9+
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - 호환성 대비
    ZoneInfo = None


class WeatherService:
    """단기 예보 CSV를 기반으로 서울 각 구의 요약 정보를 리턴한다."""

    logger = logging.getLogger(__name__)
    if ZoneInfo is not None:
        SEOUL_TZ = ZoneInfo("Asia/Seoul")
    else:
        SEOUL_TZ = datetime.timezone(datetime.timedelta(hours=9))

    API_DATA_DIR = Path(settings.BASE_DIR) / "api_data"
    CATEGORY_MAP = {
        "TMP": "temperature",
        "기온": "temperature",
        "기온(℃)": "temperature",
        "WSD": "wind_speed",
        "풍속": "wind_speed",
        "풍속(m/s)": "wind_speed",
        "PCP": "precipitation",
        "강수량": "precipitation",
        "강수량(mm)": "precipitation",
    }
    DEFAULT_SNAPSHOT = {
        "temperature": "정보없음",
        "wind_speed": "정보없음",
        "precipitation": "정보없음",
    }
    FORECAST_SLOTS: Sequence[int] = (0, 3, 6, 9, 12, 15, 18, 21)

    @classmethod
    def get_short_forecast_summary(
        cls,
        regions: Optional[Iterable[str]] = None,
        now: Optional[datetime.datetime] = None,
    ) -> Dict[str, object]:
        """단기 예보 CSV에서 가장 가까운 미래 시각 데이터를 추출한다."""

        now = cls._ensure_timezone(now or datetime.datetime.now(datetime.timezone.utc))
        target_date, target_time = cls._next_forecast_slot(now)

        rows = cls._load_short_forecast_from_csv()
        if not rows:
            cls.logger.warning("단기 예보 CSV를 찾지 못했습니다.")
            return {
                "timestamp": now.isoformat(),
                "forecast_date": target_date,
                "forecast_time": target_time,
                "display_date": cls._format_display_date(target_date),
                "display_time": cls._format_display_time(target_time),
                "regions": {},
            }

        region_names = cls._resolve_regions(regions)
        summary: Dict[str, Dict[str, str]] = {}

        for region in region_names:
            snapshot = cls._extract_region_snapshot(rows, region, target_date, target_time)
            if snapshot is None:
                snapshot = cls._latest_snapshot_for_region(rows, region)
            summary[region] = cls._merge_with_defaults(snapshot)

        return {
            "timestamp": now.isoformat(),
            "forecast_date": target_date,
            "forecast_time": target_time,
            "display_date": cls._format_display_date(target_date),
            "display_time": cls._format_display_time(target_time),
            "regions": summary,
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def _ensure_timezone(cls, dt: datetime.datetime) -> datetime.datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.timezone.utc).astimezone(cls.SEOUL_TZ)
        return dt.astimezone(cls.SEOUL_TZ)

    @classmethod
    def _resolve_regions(cls, regions: Optional[Iterable[str]]) -> List[str]:
        if regions is None:
            return list(SEOUL_GU.keys())

        if isinstance(regions, str):
            regions = [regions]

        resolved: List[str] = []
        for name in regions:
            if not name:
                continue
            cleaned = name.strip()
            if not cleaned.endswith("구"):
                cleaned = f"{cleaned}구"
            if cleaned in SEOUL_GU:
                resolved.append(cleaned)
        return resolved or list(SEOUL_GU.keys())

    @classmethod
    def _next_forecast_slot(cls, now: datetime.datetime) -> Tuple[str, str]:
        current_hour = now.hour
        target_hour = None
        for slot in cls.FORECAST_SLOTS:
            if current_hour < slot:
                target_hour = slot
                target_date = now.date()
                break
            if current_hour == slot and now.minute == 0:
                target_hour = slot
                target_date = now.date()
                break
        else:
            target_hour = cls.FORECAST_SLOTS[0]
            target_date = now.date() + datetime.timedelta(days=1)

        return target_date.strftime("%Y%m%d"), f"{target_hour:02d}00"

    @classmethod
    def _extract_region_snapshot(
        cls,
        rows: List[Dict[str, str]],
        region: str,
        target_date: str,
        target_time: str,
    ) -> Optional[Dict[str, str]]:
        snapshot: Dict[str, str] = {}
        for row in rows:
            if row.get("지역") != region:
                continue
            if row.get("날짜") != target_date or row.get("시간") != target_time:
                continue

            category = row.get("항목")
            value = row.get("값")
            key = cls.CATEGORY_MAP.get(category)
            if key:
                snapshot[key] = value

        return snapshot or None

    @classmethod
    def _latest_snapshot_for_region(
        cls,
        rows: List[Dict[str, str]],
        region: str,
    ) -> Dict[str, str]:
        latest_timestamp = ""
        latest_rows: List[Dict[str, str]] = []
        for row in rows:
            if row.get("지역") != region:
                continue
            timestamp = f"{row.get('날짜','')}{row.get('시간','')}"
            if not timestamp:
                continue
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_rows = [row]
            elif timestamp == latest_timestamp:
                latest_rows.append(row)

        snapshot: Dict[str, str] = {}
        for row in latest_rows:
            key = cls.CATEGORY_MAP.get(row.get("항목"))
            if key:
                snapshot[key] = row.get("값")
        return snapshot

    @classmethod
    def _merge_with_defaults(cls, snapshot: Optional[Dict[str, str]]) -> Dict[str, str]:
        merged = dict(cls.DEFAULT_SNAPSHOT)
        if snapshot:
            merged.update({k: v for k, v in snapshot.items() if v not in (None, "")})
        return merged

    @classmethod
    def _load_short_forecast_from_csv(cls) -> List[Dict[str, str]]:
        latest_path = cls.API_DATA_DIR / "seoul_short_latest.csv"
        if not latest_path.exists():
            cls.logger.warning("예보 CSV 파일이 없습니다: %s", latest_path)
            return []

        try:
            with latest_path.open(encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                return [cls._normalize_row(row) for row in reader]
        except Exception as exc:  # pragma: no cover - 파일 오류 대비
            cls.logger.warning("예보 CSV 읽기 실패(%s): %s", latest_path, exc)
            return []

    @staticmethod
    def _normalize_row(row: Dict[str, str]) -> Dict[str, str]:
        normalized: Dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            clean_key = key.lstrip("\ufeff").strip()
            normalized[clean_key] = value.strip() if isinstance(value, str) else value
        return normalized

    @staticmethod
    def _format_display_date(date_string: str) -> str:
        try:
            dt = datetime.datetime.strptime(date_string, "%Y%m%d").date()
        except ValueError:
            return date_string

        today = datetime.date.today()
        if dt == today:
            return "오늘"
        if dt == today + datetime.timedelta(days=1):
            return "내일"
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def _format_display_time(time_string: str) -> str:
        if len(time_string) != 4:
            return time_string
        return f"{time_string[:2]}:{time_string[2:]}"
