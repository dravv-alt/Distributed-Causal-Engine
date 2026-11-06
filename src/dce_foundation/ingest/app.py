"""FastAPI OTLP/HTTP receiver. Intended for a local attachment demonstration."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import Response
from google.rpc import status_pb2

from .otlp import OtlpDecodeError, decode_metadata, success_response
from .store import IntakeStore, StoreUnavailable

PROTOBUF_CONTENT_TYPE = "application/x-protobuf"


def _status_response(status: int, message: str) -> Response:
    body = status_pb2.Status(message=message).SerializeToString()
    return Response(body, status_code=status, media_type=PROTOBUF_CONTENT_TYPE)


def create_app(store_path: str | Path | None = None, max_payload_bytes: int = 4 * 1024 * 1024,
               max_database_bytes: int = 128 * 1024 * 1024) -> FastAPI:
    path = Path(store_path or os.environ.get("DCE_INTAKE_DB", "data/raw/intake/dce-intake.sqlite3"))
    store = IntakeStore(path, max_database_bytes)
    store.initialize()
    app = FastAPI(title="DCE OTLP Intake", version="0.1.0")
    app.state.store = store
    app.state.accepted_requests = 0
    app.state.rejected_requests = 0

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "storage": store.stats()}

    async def accept(request: Request, signal: str) -> Response:
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
        if content_type != PROTOBUF_CONTENT_TYPE:
            app.state.rejected_requests += 1
            return _status_response(415, "only application/x-protobuf is supported by this intake slice")
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > max_payload_bytes):
            app.state.rejected_requests += 1
            return _status_response(413, "payload exceeds configured limit")
        payload = await request.body()
        if len(payload) > max_payload_bytes:
            app.state.rejected_requests += 1
            return _status_response(413, "payload exceeds configured limit")
        try:
            metadata = decode_metadata(signal, payload)
        except OtlpDecodeError as exc:
            app.state.rejected_requests += 1
            return _status_response(400, str(exc))
        try:
            store.append(metadata, payload)
        except StoreUnavailable as exc:
            app.state.rejected_requests += 1
            # 503 is retryable for OTLP/HTTP exporters. No success has been sent.
            return _status_response(503, str(exc))
        app.state.accepted_requests += 1
        return Response(success_response(signal), status_code=200, media_type=PROTOBUF_CONTENT_TYPE)

    @app.post("/v1/metrics")
    async def metrics(request: Request):
        return await accept(request, "metrics")

    @app.post("/v1/traces")
    async def traces(request: Request):
        return await accept(request, "traces")

    return app


app = create_app()
