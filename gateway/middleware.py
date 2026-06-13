"""Starlette/FastAPI middleware that validates JSON request bodies.

Usage
-----
    from fastapi import FastAPI
    from gateway.middleware import PayloadValidationMiddleware

    app = FastAPI()
    app.add_middleware(PayloadValidationMiddleware, paths=["/pay", "/checkout"])

Only requests with a method in ``methods`` (default POST/PUT/PATCH) and a JSON
content type are validated. On failure the middleware short-circuits with a
``422`` response listing every error; valid requests pass through unchanged.
"""

from __future__ import annotations

import json
from typing import Iterable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .validation import PayloadValidator, ValidationError


class PayloadValidationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        validator: Optional[PayloadValidator] = None,
        paths: Optional[Iterable[str]] = None,
        methods: Iterable[str] = ("POST", "PUT", "PATCH"),
        max_body_bytes: int = 64 * 1024,
    ) -> None:
        super().__init__(app)
        self.validator = validator or PayloadValidator()
        # If paths is None, every matching method is validated.
        self.paths = tuple(paths) if paths is not None else None
        self.methods = {m.upper() for m in methods}
        self.max_body_bytes = max_body_bytes

    def _applies(self, request: Request) -> bool:
        if request.method.upper() not in self.methods:
            return False
        if self.paths is not None and not any(
            request.url.path.startswith(p) for p in self.paths
        ):
            return False
        content_type = request.headers.get("content-type", "")
        return content_type.startswith("application/json")

    async def dispatch(self, request: Request, call_next):
        if not self._applies(request):
            return await call_next(request)

        body = await request.body()
        if len(body) > self.max_body_bytes:
            return JSONResponse(
                {"detail": "payload too large"}, status_code=413
            )

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return JSONResponse(
                {"detail": "invalid JSON body"}, status_code=400
            )

        try:
            self.validator.validate(payload)
        except ValidationError as exc:
            return JSONResponse(
                {"detail": "payload validation failed", "errors": exc.errors},
                status_code=422,
            )

        # Re-attach the consumed body so downstream handlers can read it again.
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive
        return await call_next(request)
