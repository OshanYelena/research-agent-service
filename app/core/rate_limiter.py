import time
from collections import defaultdict, deque

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self):
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        if not settings.RATE_LIMIT_ENABLED:
            return True, settings.RATE_LIMIT_REQUESTS

        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

        request_times = self.requests[key]

        while request_times and request_times[0] < window_start:
            request_times.popleft()

        if len(request_times) >= settings.RATE_LIMIT_REQUESTS:
            remaining = 0
            return False, remaining

        request_times.append(now)

        remaining = settings.RATE_LIMIT_REQUESTS - len(request_times)
        return True, remaining


rate_limiter = InMemoryRateLimiter()