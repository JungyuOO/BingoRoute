import csv
import csv
import datetime
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

from django.conf import settings

from .weather_api import SEOUL_GU, get_current_weather, get_short_forecast, get_mid_forecast


@dataclass(frozen=True)
class Region:
    """Simple data holder for region metadata."""

    name: str
    nx: int
    ny: int


class WeatherService:
    """날씨 데이터 수집 및 CSV 저장/조회 서비스"""
    logger = logging.getLogger(__name__)
    SEOUL_TZ = ZoneInfo("Asia/Seoul")
    DEFAULT_MID_FORECAST_REGION_ID = "11B10101"  # 서울 및 수도권
    MID_FORECAST_REGION_IDS = {
        "서울": "11B10101",
        "서울특별시": "11B10101",
        "수도권": "11B10101",
    }

    INTEREST_CATEGORIES = {"TMP", "WSD", "PCP"}
    API_DATA_DIR = Path(settings.BASE_DIR) / "api_data"
    CURRENT_CACHE_TTL_SECONDS = 600
    _current_weather_cache: Dict[str, Optional[Any]] = {
        "timestamp": None,
        "data": None,
    }

    @staticmethod
    def get_current_weather_summary(regions: Optional[Iterable[str]] = None) -> Dict[str, Dict[str, str]]:
        """
        서울 25개 구(또는 선택된 구)의 현재 관측값을 반환.

        Returns:
            dict: {"강남구": {"기온(℃)": "...", "습도(%)": "...", ...}, ...}
        """
        now = datetime.datetime.now(WeatherService.SEOUL_TZ)
        cache = WeatherService._current_weather_cache

        if WeatherService._should_refresh_cache(cache.get("timestamp"), now):
            WeatherService.logger.info("Refreshing current weather cache from KMA API.")
            cache["data"] = WeatherService._fetch_current_weather_snapshot(now)
            cache["timestamp"] = now

        summary: Dict[str, Dict[str, str]] = cache.get("data") or {}

        if not regions:
            return summary

        filtered: Dict[str, Dict[str, str]] = {}
        for region in WeatherService._iter_regions(regions):
            filtered[region.name] = summary.get(
                region.name,
                WeatherService._merge_with_defaults({}, {"forecast_time": now.strftime("%H%M"), "seoul_time": now.isoformat()}),
            )

        return filtered

    @staticmethod
    def get_weather_forecast(region: Optional[str] = None, days: int = 3) -> List[Dict[str, str]]:
        """
        단기 예보 조회.

        Args:
            region: 특정 구만 조회하고 싶을 때 이름(강남구 등)
            days: 오늘 포함 며칠치 데이터를 가져올지 (기본 3일)
        """
        days = max(1, min(days, 7))
        regions_meta = list(WeatherService._iter_regions(region))
        target_dates = WeatherService._target_dates(days)
        forecast_rows: List[Dict[str, str]] = []

        for region_meta in regions_meta:
            try:
                forecast_items = get_short_forecast(region_meta.nx, region_meta.ny)
            except Exception as exc:  # pragma: no cover - 네트워크 예외 대비
                WeatherService.logger.warning("단기 예보 조회 실패 (%s): %s", region_meta.name, exc)
                forecast_rows.clear()
                break

            if not forecast_items:
                WeatherService.logger.warning("단기 예보 API 응답이 비었습니다. (region=%s)", region_meta.name)
                forecast_rows.clear()
                break

            for item in forecast_items:
                if item.get("예보일자") not in target_dates:
                    continue
                category = item.get("항목") or item.get("category")
                if category not in WeatherService.INTEREST_CATEGORIES:
                    continue
                value = item.get("값") or item.get("fcstValue")
                forecast_rows.append(
                    {
                        "지역": region_meta.name,
                        "날짜": item.get("예보일자") or item.get("fcstDate"),
                        "시간": item.get("예보시간") or item.get("fcstTime"),
                        "항목": category,
                        "값": value,
                    }
                )

        if forecast_rows:
            return forecast_rows

        fallback_rows = WeatherService._fallback_short_forecast_from_csv(
            regions_meta,
            target_dates,
        )
        if fallback_rows:
            WeatherService.logger.info("단기 예보 API 실패로 CSV 데이터를 사용합니다.")
        return fallback_rows

    @staticmethod
    def collect_and_save_to_csv():
        """API에서 날씨 데이터를 수집하고 CSV 대신 결과 개수 요약을 반환."""
        WeatherService.API_DATA_DIR.mkdir(parents=True, exist_ok=True)

        short_data = WeatherService.get_weather_forecast(days=3)
        mid_data_raw = WeatherService.get_mid_forecast_for_algorithm(raw=True)

        short_path = WeatherService.API_DATA_DIR / "seoul_short_latest.csv"
        mid_path = WeatherService.API_DATA_DIR / "seoul_mid_latest.csv"

        WeatherService._write_csv(
            short_path,
            short_data,
            fieldnames=["지역", "날짜", "시간", "항목", "값"],
        )

        WeatherService._write_csv(
            mid_path,
            WeatherService._prepare_mid_rows_for_csv(mid_data_raw),
            fieldnames=["지역", "타입", "날짜", "시간", "항목", "값"],
        )

        WeatherService._prune_old_csvs({short_path.resolve(), mid_path.resolve()})

        WeatherService.logger.info(
            "Weather data snapshot stored (short=%s, mid=%s)",
            len(short_data),
            len(mid_data_raw),
        )

        return {
            "short_file": str(short_path),
            "mid_file": str(mid_path),
            "short_count": len(short_data),
            "mid_count": len(mid_data_raw),
        }

    @staticmethod
    def cleanup_old_csv_files(days=7):
        """오래된 CSV 파일들 정리"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return
        return  # 추후 주석처리 원복할 때 삭제 예정

        # cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        # deleted_count = 0
        #
        # for filename in os.listdir(api_data_dir):
        #     if filename.endswith('.csv') and filename != '.gitkeep':
        #         file_path = os.path.join(api_data_dir, filename)
        #         file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        #
        #         if file_time < cutoff_time:
        #             try:
        #                 os.remove(file_path)
        #                 deleted_count += 1
        #                 print(f"🗑️ 오래된 CSV 파일 삭제: {filename}")
        #             except Exception as e:
        #                 print(f"❌ CSV 파일 삭제 실패: {filename} - {e}")
        #
        # if deleted_count > 0:
        #     print(f"✅ 총 {deleted_count}개의 오래된 CSV 파일을 정리했습니다.")

    @staticmethod
    def delete_csv_files(file_paths):
        """지정된 CSV 파일들 삭제"""
        return  # 추후 주석처리 원복할 때 삭제 예정
        # for file_path in file_paths:
        #     if file_path and os.path.exists(file_path):
        #         try:
        #             os.remove(file_path)
        #             print(f"🗑️ CSV 파일 삭제: {os.path.basename(file_path)}")
        #         except Exception as e:
        #             print(f"❌ CSV 파일 삭제 실패: {file_path} - {e}")
    #

    @staticmethod
    def _get_latest_weather_csv():
        """가장 최신의 날씨 CSV 파일 경로 반환"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return None
        # CSV 더미 데이터 탐색 비활성화
        return None

    def _get_latest_mid_csv():
        """가장 최신의 중기예보 CSV 파일 경로 반환"""
        api_data_dir = os.path.join(settings.BASE_DIR, 'api_data')
        if not os.path.exists(api_data_dir):
            return None
        # CSV 더미 데이터 탐색 비활성화
        return None

    @staticmethod
    def get_weather_statistics():
        """날씨 데이터 통계 조회 (CSV 기반)"""
        short_count = len(WeatherService.get_weather_forecast(days=3))
        mid_count = len(WeatherService.get_mid_forecast_for_algorithm(raw=True))
        regions = len(list(WeatherService._iter_regions()))
        now = datetime.datetime.now(WeatherService.SEOUL_TZ).isoformat()

        return {
            "short_forecast": short_count,
            "mid_forecast": mid_count,
            "legacy_data": 0,
            "total": short_count + mid_count,
            "regions": regions,
            "last_updated": now,
        }

    @staticmethod
    def get_weather_by_time(target_date: Optional[str] = None, target_time: Optional[str] = None):
        """특정 시간대의 서울 구별 날씨 조회"""
        now = datetime.datetime.now(WeatherService.SEOUL_TZ)

        if not target_date:
            target_date = now.strftime("%Y%m%d")

        if not target_time:
            target_time = WeatherService._nearest_forecast_time(now)

        snapshots: List[Dict[str, str]] = []
        consecutive_failures = 0
        for region_meta in WeatherService._iter_regions():
            try:
                forecast_items = get_short_forecast(region_meta.nx, region_meta.ny)
            except Exception as exc:  # pragma: no cover - 네트워크 예외 대비
                WeatherService.logger.warning("시간대별 예보 조회 실패 (%s): %s", region_meta.name, exc)
                consecutive_failures += 1
                if consecutive_failures >= 1:
                    WeatherService.logger.warning(
                        "시간대별 예보 API 연속 실패로 CSV 데이터를 사용합니다."
                    )
                    return WeatherService._fallback_weather_by_time_from_csv(target_date, target_time)
                continue
            else:
                if not forecast_items:
                    consecutive_failures += 1
                    WeatherService.logger.warning(
                        "시간대별 예보 API 응답이 비었습니다. (region=%s, 실패 횟수=%s)",
                        region_meta.name,
                        consecutive_failures,
                    )
                    if consecutive_failures >= 1:
                        WeatherService.logger.warning(
                            "시간대별 예보 API 연속 실패로 CSV 데이터를 사용합니다."
                        )
                        return WeatherService._fallback_weather_by_time_from_csv(target_date, target_time)
                    continue
                consecutive_failures = 0

            snapshot = {
                "region": region_meta.name,
                "date": target_date,
                "time": target_time,
                "temperature": "정보없음",
                "wind_speed": "정보없음",
                "precipitation": "정보없음",
            }

            for item in forecast_items:
                if (item.get("예보일자") or item.get("fcstDate")) != target_date:
                    continue
                if (item.get("예보시간") or item.get("fcstTime")) != target_time:
                    continue

                category = item.get("항목") or item.get("category")
                value = item.get("값") or item.get("fcstValue")

                if category in ("TMP", "기온"):
                    snapshot["temperature"] = value
                elif category in ("WSD", "풍속"):
                    snapshot["wind_speed"] = value
                elif category in ("PCP", "강수량"):
                    snapshot["precipitation"] = value

            snapshots.append(snapshot)

        if WeatherService._is_snapshot_empty(snapshots):
            fallback = WeatherService._fallback_weather_by_time_from_csv(target_date, target_time)
            if fallback:
                WeatherService.logger.info(
                    "시간대별 예보 API 실패로 CSV 데이터를 사용합니다. (date=%s, time=%s)",
                    target_date,
                    target_time,
                )
                return fallback

        return snapshots

    @staticmethod
    def _format_date(date_string):
        """날짜 포맷팅 유틸리티"""
        if not date_string or len(date_string) != 8:
            return date_string

        year = date_string[:4]
        month = date_string[4:6]
        day = date_string[6:8]

        today = datetime.date.today()
        target_date = datetime.date(int(year), int(month), int(day))

        if target_date == today:
            return '오늘'
        elif target_date == today + datetime.timedelta(days=1):
            return '내일'
        else:
            return f"{month}/{day}"

    # ---------- 내부 유틸리티 ----------

    @staticmethod
    def _iter_regions(region_names: Optional[Iterable[str]] = None) -> Iterable[Region]:
        if region_names is None:
            items = SEOUL_GU.items()
        else:
            if isinstance(region_names, str):
                region_iterable = [region_names]
            else:
                region_iterable = list(region_names)

            if not region_iterable:
                items = SEOUL_GU.items()
            else:
                normalized = set()
                for name in region_iterable:
                    if not name:
                        continue
                    cleaned = name.strip()
                    if not cleaned.endswith("구"):
                        cleaned = f"{cleaned}구"
                    normalized.add(cleaned)

                items = [(name, SEOUL_GU[name]) for name in normalized if name in SEOUL_GU]
                if not items:
                    items = SEOUL_GU.items()

        for name, (nx, ny) in items:
            yield Region(name=name, nx=nx, ny=ny)

    @staticmethod
    def _target_dates(days: int) -> List[str]:
        today = datetime.datetime.now(WeatherService.SEOUL_TZ).date()
        return [
            (today + datetime.timedelta(days=offset)).strftime("%Y%m%d")
            for offset in range(days)
        ]

    @staticmethod
    def _nearest_forecast_time(now: datetime.datetime) -> str:
        forecast_hours = [0, 3, 6, 9, 12, 15, 18, 21]
        closest_hour = min(forecast_hours, key=lambda h: abs(h - now.hour))
        return f"{closest_hour:02d}00"

    @staticmethod
    def _merge_with_defaults(
        current: Dict[str, str],
        extra: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        defaults = {
            "기온(℃)": "정보없음",
            "습도(%)": "정보없음",
            "풍속(m/s)": "정보없음",
            "강수량(mm)": "0",
        }
        merged = {**defaults, **current}
        if extra:
            merged.update(extra)
        return merged

    @staticmethod
    def _should_refresh_cache(timestamp: Optional[datetime.datetime], now: datetime.datetime) -> bool:
        if not timestamp:
            return True
        delta = now - timestamp
        return delta.total_seconds() >= WeatherService.CURRENT_CACHE_TTL_SECONDS

    @staticmethod
    def _fetch_current_weather_snapshot(reference_time: datetime.datetime) -> Dict[str, Dict[str, str]]:
        timestamp = reference_time.isoformat()
        forecast_time = reference_time.strftime("%H%M")
        summary: Dict[str, Dict[str, str]] = {}
        has_live_data = False

        consecutive_failures = 0
        for region in WeatherService._iter_regions():
            try:
                current = get_current_weather(region.nx, region.ny) or {}
            except Exception as exc:  # pragma: no cover - 네트워크 예외 대비
                WeatherService.logger.warning("현재 날씨 조회 실패 (%s): %s", region.name, exc)
                current = {}

            if current:
                has_live_data = True
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                WeatherService.logger.warning(
                    "현재 날씨 API 응답이 비어 있습니다. (region=%s, 실패 횟수=%s)",
                    region.name,
                    consecutive_failures,
                )
                if consecutive_failures >= 1:
                    WeatherService.logger.warning(
                        "현재 날씨 API 연속 실패로 CSV 데이터로 대체합니다."
                    )
                    return WeatherService._fallback_current_weather_from_csv(reference_time)
                current = {}

            summary[region.name] = WeatherService._merge_with_defaults(
                current,
                {
                    "forecast_time": forecast_time,
                    "seoul_time": timestamp,
                },
            )

        if has_live_data:
            return summary

        fallback = WeatherService._fallback_current_weather_from_csv(reference_time)
        if fallback:
            WeatherService.logger.info(
                "현재 날씨 API 응답 실패로 CSV 데이터로 대체합니다. (timestamp=%s)",
                timestamp,
            )
            return fallback

        return summary

    @staticmethod
    def _resolve_mid_region_id(region: Optional[str]) -> str:
        if not region:
            return WeatherService.DEFAULT_MID_FORECAST_REGION_ID

        key = region.strip()
        return WeatherService.MID_FORECAST_REGION_IDS.get(
            key,
            WeatherService.DEFAULT_MID_FORECAST_REGION_ID,
        )

    @staticmethod
    def _format_mid_forecast(raw_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        formatted: Dict[Tuple[str, str], Dict[str, str]] = {}

        for item in raw_items:
            date = item.get("날짜")
            period = item.get("시간", "")
            key = (date, period)

            entry = formatted.setdefault(
                key,
                {
                    "date": date,
                    "region": item.get("지역", "서울"),
                    "period": period,
                    "weather_condition": None,
                    "rain_probability": None,
                    "min_temperature": None,
                    "max_temperature": None,
                },
            )

            category = item.get("항목")
            value = item.get("값")

            if category == "날씨":
                entry["weather_condition"] = value
            elif category == "강수확률(%)":
                entry["rain_probability"] = WeatherService._safe_cast(value)
            elif category == "최저기온(℃)":
                entry["min_temperature"] = WeatherService._safe_cast(value)
            elif category == "최고기온(℃)":
                entry["max_temperature"] = WeatherService._safe_cast(value)

        return list(formatted.values())

    @staticmethod
    def _safe_cast(value: Optional[str]) -> Optional[float]:
        if value in (None, "-", "nan"):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def get_mid_forecast_for_algorithm(raw: bool = False, region: Optional[str] = None):
        """중기예보 원시/가공 데이터를 선택적으로 반환"""
        region_id = WeatherService._resolve_mid_region_id(region)

        try:
            mid_items = get_mid_forecast(region_id)
        except Exception as exc:  # pragma: no cover - 네트워크 예외 대비
            print(f"❌ 중기예보 조회 오류: {exc}")
            mid_items = []

        if not mid_items:
            fallback = WeatherService._load_mid_forecast_from_csv(region)
            if fallback:
                WeatherService.logger.info("중기 예보 API 실패로 CSV 데이터를 사용합니다.")
                mid_items = fallback

        if raw:
            # 원본 목록에 지역 정보 주입
            for item in mid_items:
                item.setdefault("지역", region or "서울")
            return mid_items

        return WeatherService._format_mid_forecast(mid_items)

    # ---------- CSV Fallbacks ----------

    @staticmethod
    def _fallback_current_weather_from_csv(reference_time: datetime.datetime) -> Dict[str, Dict[str, str]]:
        rows = WeatherService._load_short_forecast_from_csv()
        if not rows:
            return {}

        latest_entries = WeatherService._latest_short_entries_by_region(rows)
        if not latest_entries:
            return {}

        summary: Dict[str, Dict[str, str]] = {}
        timestamp = reference_time.isoformat()

        for region, entries in latest_entries.items():
            data = WeatherService._merge_with_defaults(
                {},
                {
                    "forecast_time": entries[0].get("시간", ""),
                    "seoul_time": timestamp,
                },
            )
            for entry in entries:
                category = entry.get("항목")
                value = entry.get("값")
                if category in ("TMP", "기온", "기온(℃)"):
                    data["기온(℃)"] = value
                elif category in ("REH", "습도", "습도(%)"):
                    data["습도(%)"] = value
                elif category in ("WSD", "풍속", "풍속(m/s)"):
                    data["풍속(m/s)"] = value
                elif category in ("PCP", "강수량", "강수량(mm)"):
                    data["강수량(mm)"] = value
            summary[region] = data

        return summary

    @staticmethod
    def _fallback_short_forecast_from_csv(
        regions_meta: List[Region],
        target_dates: List[str],
    ) -> List[Dict[str, str]]:
        rows = WeatherService._load_short_forecast_from_csv()
        if not rows:
            return []

        region_names = {region_meta.name for region_meta in regions_meta} if regions_meta else None
        results: List[Dict[str, str]] = []

        for row in rows:
            region = row.get("지역")
            if region_names and region not in region_names:
                continue
            if target_dates and row.get("날짜") not in target_dates:
                continue

            category = row.get("항목")
            if category not in WeatherService.INTEREST_CATEGORIES:
                continue

            results.append(
                {
                    "지역": region,
                    "날짜": row.get("날짜"),
                    "시간": row.get("시간"),
                    "항목": category,
                    "값": row.get("값"),
                }
            )

        if not results and target_dates:
            # 최신 데이터라도 제공하기 위해 날짜 필터를 무시한 결과 재구성
            for row in rows:
                region = row.get("지역")
                if region_names and region not in region_names:
                    continue
                category = row.get("항목")
                if category not in WeatherService.INTEREST_CATEGORIES:
                    continue
                results.append(
                    {
                        "지역": region,
                        "날짜": row.get("날짜"),
                        "시간": row.get("시간"),
                        "항목": category,
                        "값": row.get("값"),
                    }
                )

        return results

    @staticmethod
    def _fallback_weather_by_time_from_csv(target_date: str, target_time: str) -> List[Dict[str, str]]:
        rows = WeatherService._load_short_forecast_from_csv()
        if not rows:
            return []

        filtered: Dict[str, Dict[str, str]] = {}
        for row in rows:
            if row.get("날짜") != target_date or row.get("시간") != target_time:
                continue
            region = row.get("지역")
            if not region:
                continue

            entry = filtered.setdefault(
                region,
                {
                    "region": region,
                    "date": target_date,
                    "time": target_time,
                    "temperature": "정보없음",
                    "wind_speed": "정보없음",
                    "precipitation": "정보없음",
                },
            )

            category = row.get("항목")
            value = row.get("값")
            if category in ("TMP", "기온", "기온(℃)"):
                entry["temperature"] = value
            elif category in ("WSD", "풍속", "풍속(m/s)"):
                entry["wind_speed"] = value
            elif category in ("PCP", "강수량", "강수량(mm)"):
                entry["precipitation"] = value

        if filtered:
            return list(filtered.values())

        # 데이터가 없으면 최신 타임스탬프 기준으로 생성
        latest_entries = WeatherService._latest_short_entries_by_region(rows)
        snapshots: List[Dict[str, str]] = []
        for region, entries in latest_entries.items():
            base = {
                "region": region,
                "date": entries[0].get("날짜"),
                "time": entries[0].get("시간"),
                "temperature": "정보없음",
                "wind_speed": "정보없음",
                "precipitation": "정보없음",
            }
            for entry in entries:
                category = entry.get("항목")
                value = entry.get("값")
                if category in ("TMP", "기온", "기온(℃)"):
                    base["temperature"] = value
                elif category in ("WSD", "풍속", "풍속(m/s)"):
                    base["wind_speed"] = value
                elif category in ("PCP", "강수량", "강수량(mm)"):
                    base["precipitation"] = value
            snapshots.append(base)

        return snapshots

    @staticmethod
    def _latest_short_entries_by_region(rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        latest: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            region = row.get("지역")
            if not region:
                continue
            timestamp = f"{row.get('날짜', '')}{row.get('시간', '')}"
            info = latest.setdefault(region, {"timestamp": None, "rows": []})

            if not info["timestamp"] or timestamp > info["timestamp"]:
                info["timestamp"] = timestamp
                info["rows"] = [row]
            elif timestamp == info["timestamp"]:
                info["rows"].append(row)

        return {region: data["rows"] for region, data in latest.items() if data["rows"]}

    @staticmethod
    def _is_snapshot_empty(snapshots: List[Dict[str, str]]) -> bool:
        if not snapshots:
            return True

        for snapshot in snapshots:
            if (
                snapshot.get("temperature") not in (None, "정보없음")
                or snapshot.get("wind_speed") not in (None, "정보없음")
                or snapshot.get("precipitation") not in (None, "정보없음")
            ):
                return False
        return True

    @staticmethod
    def _get_latest_csv(prefix: str) -> Optional[Path]:
        if not WeatherService.API_DATA_DIR.exists():
            return None

        latest_named = WeatherService.API_DATA_DIR / f"{prefix}_latest.csv"
        if latest_named.exists():
            return latest_named

        candidates = sorted(
            WeatherService.API_DATA_DIR.glob(f"{prefix}_*.csv"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        return candidates[0] if candidates else None

    @staticmethod
    def _load_short_forecast_from_csv() -> List[Dict[str, str]]:
        latest = WeatherService._get_latest_csv("seoul_short")
        if not latest:
            return []

        try:
            with latest.open(encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                return [WeatherService._normalize_csv_row(row) for row in reader]
        except Exception as exc:  # pragma: no cover - 파일 오류 대비
            WeatherService.logger.warning("단기 예보 CSV 로드 실패: %s", exc)
            return []

    @staticmethod
    def _load_mid_forecast_from_csv(region: Optional[str] = None) -> List[Dict[str, str]]:
        latest = WeatherService._get_latest_csv("seoul_mid")
        if not latest:
            return []

        try:
            with latest.open(encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                rows = [WeatherService._normalize_csv_row(row) for row in reader]
        except Exception as exc:  # pragma: no cover - 파일 오류 대비
            WeatherService.logger.warning("중기 예보 CSV 로드 실패: %s", exc)
            return []

        if region:
            region = region.strip()
            filtered = [row for row in rows if row.get("지역") == region]
            if filtered:
                return filtered

        return rows

    @staticmethod
    def _normalize_csv_row(row: Dict[str, str]) -> Dict[str, str]:
        if not row:
            return {}
        normalized = {}
        for key, value in row.items():
            if key is None:
                continue
            clean_key = key.lstrip("\ufeff").strip()
            normalized[clean_key] = value.strip() if isinstance(value, str) else value
        return normalized

    @staticmethod
    def _prepare_mid_rows_for_csv(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prepared: List[Dict[str, Any]] = []
        for item in rows:
            prepared.append(
                {
                    "지역": item.get("지역") or item.get("region") or "서울",
                    "타입": item.get("타입") or item.get("type") or "중기",
                    "날짜": item.get("날짜") or item.get("date"),
                    "시간": item.get("시간") or item.get("period"),
                    "항목": item.get("항목") or item.get("category"),
                    "값": item.get("값") or item.get("value"),
                }
            )
        return prepared

    @staticmethod
    def _write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: Iterable[str]) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: (row.get(field) or "") for field in fieldnames})

    @staticmethod
    def _prune_old_csvs(keep: Set[Path]) -> None:
        if not WeatherService.API_DATA_DIR.exists():
            return

        keep_resolved = {path.resolve() for path in keep}
        patterns = ("seoul_short_*.csv", "seoul_mid_*.csv")
        for pattern in patterns:
            for candidate in WeatherService.API_DATA_DIR.glob(pattern):
                if candidate.resolve() in keep_resolved:
                    continue
                try:
                    candidate.unlink()
                except Exception as exc:  # pragma: no cover - 파일 삭제 실패 대비
                    WeatherService.logger.warning("기존 CSV 삭제 실패 (%s): %s", candidate.name, exc)
