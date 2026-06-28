"""Rate limiting middleware for FastAPI.

Supports two backends:
- Redis (when `redis` package is available AND `REDIS_URL` env var is set)
- File-based JSON tracking (fallback for single-server multi-worker deployments)

The file-based backend uses /tmp/rate_limit/ with IP+minute buckets and
is suitable for deployments without a Redis server.
"""
import json
import os
import time
import fcntl
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Try to import redis; if unavailable we fall back to file-based tracking
try:
    import redis as _redis_lib  # noqa: F401
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False


class _FileBasedRateLimiter:
    """File-based rate limiter shared across processes on the same host.

    Uses a JSON file in /tmp/rate_limit/ with one entry per IP+minute bucket.
    File locking (fcntl) ensures atomic reads/writes across workers.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.dir = "/tmp/rate_limit"
        self.file = os.path.join(self.dir, "buckets.json")
        os.makedirs(self.dir, exist_ok=True)

    def _read_buckets(self) -> dict:
        """Read all buckets from the JSON file."""
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_buckets(self, buckets: dict) -> None:
        """Write all buckets to the JSON file atomically."""
        tmp = self.file + ".tmp"
        with open(tmp, "w") as f:
            json.dump(buckets, f)
        os.replace(tmp, self.file)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if the client IP is within rate limits. Returns True if allowed."""
        now = time.time()
        minute_key = f"{client_ip}:{int(now // 60)}"
        window_start = now - 60

        with open(self.file + ".lock", "w") as lockfile:
            fcntl.flock(lockfile, fcntl.LOCK_EX)
            try:
                buckets = self._read_buckets()

                # Clean old entries (older than 60 seconds)
                keys_to_remove = [
                    k for k, v in buckets.items()
                    if v.get("timestamp", 0) < window_start
                ]
                for k in keys_to_remove:
                    del buckets[k]

                # Check current bucket
                entry = buckets.get(minute_key, {"count": 0, "timestamp": now})
                if entry["count"] >= self.requests_per_minute:
                    self._write_buckets(buckets)
                    return False

                # Increment and save
                entry["count"] += 1
                entry["timestamp"] = now
                buckets[minute_key] = entry
                self._write_buckets(buckets)
                return True
            finally:
                fcntl.flock(lockfile, fcntl.LOCK_UN)


class _RedisRateLimiter:
    """Redis-backed rate limiter for distributed deployments."""

    def __init__(self, requests_per_minute: int = 60, redis_url: str = ""):
        import redis
        self.requests_per_minute = requests_per_minute
        self.client = redis.from_url(redis_url, decode_responses=True)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if the client IP is within rate limits using Redis INCR + TTL."""
        now = time.time()
        minute_key = f"ratelimit:{client_ip}:{int(now // 60)}"

        pipe = self.client.pipeline()
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        results = pipe.execute()

        count = results[0]
        return count <= self.requests_per_minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter that works across uvicorn workers.

    Automatically selects Redis (if available and configured) or falls back
    to a file-based implementation using /tmp/rate_limit/.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

        redis_url = os.getenv("REDIS_URL", "")
        if _REDIS_AVAILABLE and redis_url:
            self._backend = _RedisRateLimiter(requests_per_minute, redis_url)
        else:
            self._backend = _FileBasedRateLimiter(requests_per_minute)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Skip rate limiting during tests
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Check rate limit via backend
        if not self._backend.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        return response
