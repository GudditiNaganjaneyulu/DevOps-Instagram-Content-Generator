"""
OpenTelemetry → Grafana Cloud OTLP
Traces  : FastAPI requests + httpx (AI provider calls)
Metrics : Prometheus-style via OTLP
Logs    : structlog already ships JSON; future: OTLP log exporter
"""
import logging
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_telemetry(app) -> None:
    settings = get_settings()

    if not settings.otel_endpoint:
        logger.info("OTEL_ENDPOINT not set — telemetry disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        resource = Resource(attributes={
            SERVICE_NAME: "devops-runtime-emotions-api",
            "deployment.environment": settings.app_env,
            "service.version": settings.app_version,
        })

        # OTLP exporter → Grafana Cloud
        # Headers format: "Authorization=Basic <base64token>"
        headers = {}
        if settings.otel_headers:
            for part in settings.otel_headers.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    headers[k.strip()] = v.strip()

        exporter = OTLPSpanExporter(
            endpoint=f"{settings.otel_endpoint.rstrip('/')}/v1/traces",
            headers=headers,
        )

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        # Auto-instrument FastAPI (all HTTP requests get a span)
        FastAPIInstrumentor.instrument_app(app)

        # Auto-instrument httpx (all AI provider calls get child spans)
        HTTPXClientInstrumentor().instrument()

        logger.info(
            "Telemetry configured",
            endpoint=settings.otel_endpoint,
            service="devops-runtime-emotions-api",
        )

    except Exception as e:
        # Never crash the app over observability setup
        logger.warning("Telemetry setup failed — continuing without tracing", error=str(e))
