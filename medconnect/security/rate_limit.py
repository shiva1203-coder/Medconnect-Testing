import time
from collections import defaultdict, deque
from flask import request, jsonify


class InMemoryRateLimiter:
    """
    Lightweight process-local rate limiter.
    Good for development/single-process deployments.
    """

    def __init__(self):
        self._events = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        bucket = self._events[key]

        while bucket and bucket[0] <= now - window_seconds:
            bucket.popleft()

        if len(bucket) >= limit:
            return False

        bucket.append(now)
        return True


limiter = InMemoryRateLimiter()


def rate_limit(limit: int, window_seconds: int, key_fn=None):
    def decorator(fn):
        def wrapped(*args, **kwargs):
            key_base = key_fn() if key_fn else request.remote_addr or "unknown"
            key = f"{fn.__name__}:{key_base}"
            if not limiter.allow(key, limit, window_seconds):
                return jsonify({"error": "Rate limit exceeded"}), 429
            return fn(*args, **kwargs)

        wrapped.__name__ = fn.__name__
        return wrapped

    return decorator
