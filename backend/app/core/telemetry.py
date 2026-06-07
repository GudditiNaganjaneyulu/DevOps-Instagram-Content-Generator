"""
OpenTelemetry → Grafana Cloud OTLP   (traces → Tempo)
Direct Loki push                     (logs → Loki)
Metrics: future — add OTLP metric exporter when needed
"""
import json
import logging
import time
from base64 import b64encode

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _parse_headers(raw: str) -> dict:
    """Parse 'Key=Value,Key2=Value2' into a dict."""
    headers = {}
    for part in raw.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            headers[k.strip()] = v.strip()
    return headers


class _LokiHandler(logging.Handler):
    """
    Synchronous Loki push handler.
    Ships each log record to Loki immediately via httpx (fire-and-forget style).
    Safe to use in async apps — logging itself is synchronous.
    """

    def __init__(self, url: str, username: str, password: str, static_labels: dict):
        super().__init__()
        self._url = url
        self._auth = b64encode(f"{username}:{password}".encode()).decode()
        self._labels = static_labels

    def emit(self, record: logging.LogRecord) -> None:
        try:
            import httpx

            ts_ns = str(int(time.time() * 1_000_000_000))
            message = self.format(record)

            stream_labels = {
                **self._labels,
                "level": record.levelname.lower(),
            }

            payload = {
                "streams": [
                    {
                        "stream": stream_labels,
                        "values": [[ts_ns, message]],
                    }
                ]
            }

            httpx.post(
                self._url,
                content=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {self._auth}",
                },
                timeout=3.0,
            )
        except Exception:
            # Never crash the app over logging
            pass


def _setup_loki(settings) -> bool:
    if not (settings.loki_url and settings.loki_username and settings.loki_password):
        return False

    try:
        loki_handler = _LokiHandler(
            url=settings.loki_url,
            username=settings.loki_username,
            password=settings.loki_password,
            static_labels={
                "app": "devops-runtime-emotions",
                "env": settings.app_env,
                "service": "api",
            },
        )
        loki_handler.setLevel(logging.INFO)
        # structlog JSONRenderer already put everything into record.msg as a JSON
        # string — pass it through as-is so Loki can parse with | json
        loki_handler.setFormatter(logging.Formatter("%(message)s"))

        # Attach to root logger so structlog output (which writes to stdlib) is captured
        root = logging.getLogger()
        root.addHandler(loki_handler)

        logger.info("Loki log handler configured", url=settings.loki_url)
        return True
    except Exception as e:
        logger.warning("Loki handler setup failed", error=str(e))
        return False


def setup_telemetry(app) -> None:
    settings = get_settings()

    # ── Loki (logs) ────────────────────────────────────────────────────────────
    _setup_loki(settings)

    # ── OTLP (traces → Tempo) ──────────────────────────────────────────────────
    if not settings.otel_endpoint:
        logger.info("OTEL_ENDPOINT not set — trace export disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        base = settings.otel_endpoint.rstrip("/")
        headers = _parse_headers(settings.otel_headers) if settings.otel_headers else {}

        resource = Resource(attributes={
            SERVICE_NAME: "devops-runtime-emotions-api",
            "deployment.environment": settings.app_env,
            "service.version": settings.app_version,
        })

        trace_exporter = OTLPSpanExporter(
            endpoint=f"{base}/v1/traces",
            headers=headers,
        )
        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        trace.set_tracer_provider(trace_provider)

        FastAPIInstrumentor.instrument_app(app)
        HTTPXClientInstrumentor().instrument()

        logger.info("OTLP trace exporter configured", endpoint=base)

    except Exception as e:
        logger.warning("Telemetry setup failed — continuing without tracing", error=str(e))
