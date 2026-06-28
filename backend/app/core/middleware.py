"""Custom middleware: security headers, request ID, timing, caching headers."""
import time
import uuid
import hashlib
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("learnfinnish")

# Track application start time for uptime calculation
_APP_START_TIME = time.time()


def get_uptime_seconds() -> float:
    return time.time() - _APP_START_TIME


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related HTTP headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # HSTS — force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Content Security Policy (baseline)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions policy (disable unused browser features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )
        # Remove server identification
        if "server" in response.headers:
            del response.headers["server"]

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a unique request ID for distributed tracing.
    Uses incoming X-Request-ID header if present, otherwise generates one.
    Echoes the ID back in the response headers.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        logger.info(
            "method=%s path=%s status=%d request_id=%s duration=%.2fms",
            request.method, request.url.path, response.status_code,
            request_id, elapsed_ms,
        )
        return response


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add ETag and Cache-Control headers to GET responses.
    Supports conditional requests via If-None-Match.
    """

    CACHEABLE_PATH_PREFIXES = ("/api/v1/words", "/api/v1/grammar")
    # Do NOT cache authenticated/user-specific endpoints
    NON_CACHEABLE_PREFIXES = ("/api/v1/srs/due", "/api/v1/progress", "/api/v1/auth/me")

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if request.method != "GET":
            return response

        path = request.url.path

        # Skip non-cacheable paths
        if any(path.startswith(p) for p in self.NON_CACHEABLE_PREFIXES):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            return response

        # Add caching headers for cacheable paths
        if any(path.startswith(p) for p in self.CACHEABLE_PATH_PREFIXES):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            etag = hashlib.md5(body).hexdigest()

            # Check If-None-Match
            if_none_match = request.headers.get("If-None-Match")
            if if_none_match and if_none_match.strip('"') == etag:
                return Response(
                    status_code=304,
                    headers={
                        "ETag": f'"{etag}"',
                        "Cache-Control": "public, max-age=3600",
                    },
                )

            response.headers["ETag"] = f'"{etag}"'
            response.headers["Cache-Control"] = "public, max-age=3600"
            response = Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        else:
            # Default: prevent caching for API responses unless explicitly set
            if "Cache-Control" not in response.headers:
                response.headers["Cache-Control"] = "no-store"

        return response


def get_app_uptime() -> float:
    """Return uptime in seconds."""
    return time.time() - _APP_START_TIME
