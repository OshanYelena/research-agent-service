import logging
import structlog

from app.core.config import settings


def configure_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(message)s",
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
    )


logger = structlog.get_logger()