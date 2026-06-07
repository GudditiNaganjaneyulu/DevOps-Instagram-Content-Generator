import logging
import structlog
from app.config import get_settings


def configure_logging() -> None:
    settings = get_settings()

    log_level = logging.DEBUG if settings.app_debug else logging.INFO

    # add_logger_name only works with stdlib.LoggerFactory (accesses logger.name).
    # PrintLoggerFactory gives a PrintLogger which has no .name → AttributeError.
    # So it lives in the production branch only.
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.is_production:
        # Route through stdlib so handlers (LokiHandler, etc.) receive structured logs.
        # Final processor renders each record as a JSON string → record.msg = '{"event":...}'
        structlog.configure(
            processors=shared_processors + [
                structlog.stdlib.add_logger_name,  # safe here — stdlib.LoggerFactory gives real Logger
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(log_level)
        # Plain stdout handler — format is just %(message)s because structlog
        # already rendered the full JSON into the message field
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(stream_handler)
    else:
        structlog.configure(
            processors=shared_processors + [structlog.dev.ConsoleRenderer()],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(level=log_level)

    for noisy in ("pymongo", "motor", "httpx", "httpcore", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
