"""Rate limiting middleware for EdilEngine API."""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware per IP address.

    Tracks request counts per IP within a sliding time window.
    For production use, replace with Redis-based rate limiting.
    """

    def __init__(self, app, max_requests: int | None = None, window_seconds: int | None = None) -> None:
        super().__init__(app)
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        # {ip: [(timestamp, count), ...]}
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _clean_old_requests(self, ip: str) -> None:
        """Remove requests outside the current time window."""
        now = time.time()
        cutoff = now - self.window_seconds
        self._requests[ip] = [
            ts for ts in self._requests[ip] if ts > cutoff
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> JSONResponse:
        """Process request with rate limiting check."""
        # Get client IP (handle X-Forwarded-For for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)

        self._clean_old_requests(client_ip)

        if len(self._requests[client_ip]) >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: "
                f"{len(self._requests[client_ip])} requests in {self.window_seconds}s"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after_seconds": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Window": str(self.window_seconds),
                },
            )

        # Record this request
        self._requests[client_ip].append(time.time())

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.max_requests - len(self._requests[client_ip]))
        )
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

        return response  # type: ignore[return-value]
