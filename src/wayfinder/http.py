import hashlib
import json
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from wayfinder.config import settings

DEFAULT_CACHE_DIR = Path(".cache/http")

HOST_MIN_INTERVAL_S = {"nominatim.openstreetmap.org": 1.0}
DEFAULT_MIN_INTERVAL_S = 0.1

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    return (
        isinstance(exc, httpx.HTTPStatusError)
        and exc.response.status_code in RETRYABLE_STATUS
    )


class RateLimiter:
    def __init__(self, min_interval_s: float) -> None:
        self._min_interval_s = min_interval_s
        self._last_call = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            remaining = self._min_interval_s - (time.monotonic() - self._last_call)
            if remaining > 0:
                time.sleep(remaining)
            self._last_call = time.monotonic()


class CachedClient:
    def __init__(
        self,
        cache_dir: Path = DEFAULT_CACHE_DIR,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._limiters: dict[str, RateLimiter] = {}
        self._limiters_lock = threading.Lock()
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": settings.user_agent},
            transport=transport,
        )

    def _limiter_for(self, url: str) -> RateLimiter:
        host = urlparse(url).netloc
        with self._limiters_lock:
            if host not in self._limiters:
                interval = HOST_MIN_INTERVAL_S.get(host, DEFAULT_MIN_INTERVAL_S)
                self._limiters[host] = RateLimiter(interval)
            return self._limiters[host]

    def _cache_path(self, method: str, url: str, payload: str) -> Path:
        digest = hashlib.sha256(f"{method}|{url}|{payload}".encode()).hexdigest()
        return self._cache_dir / f"{digest}.json"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    def _fetch(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
    ) -> dict | list:
        self._limiter_for(url).wait()
        response = self._client.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def _cached(
        self,
        method: str,
        url: str,
        payload: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
    ) -> dict | list:
        path = self._cache_path(method, url, payload)
        if path.exists():
            return json.loads(path.read_text())

        value = self._fetch(method, url, params=params, data=data)
        path.write_text(json.dumps(value))
        return value

    def get_json(self, url: str, params: dict | None = None) -> dict | list:
        payload = json.dumps(params or {}, sort_keys=True)
        return self._cached("GET", url, payload, params=params)

    def post_form(self, url: str, data: dict[str, str]) -> dict:
        payload = json.dumps(data, sort_keys=True)
        return self._cached("POST", url, payload, data=data)
