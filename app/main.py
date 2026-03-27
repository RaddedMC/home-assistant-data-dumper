import logging
import signal
import sys

from app.config import load_config
from app.database import Database
from app.ha_client import HomeAssistantClient
from app.ingestion import IngestionService
from app.web import create_app


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> int:
    config = load_config()
    configure_logging(config.log_level)

    logger = logging.getLogger(__name__)

    if not config.supervisor_token:
        logger.warning("SUPERVISOR_TOKEN is empty; Home Assistant API calls are expected to fail")

    db = Database(config.db_path)
    db.initialize()

    ha_client = HomeAssistantClient(config.ha_api_base, config.supervisor_token)
    ingestion = IngestionService(
        db=db,
        ha_client=ha_client,
        poll_interval_seconds=config.poll_interval_seconds,
        history_chunk_hours=config.history_chunk_hours,
    )
    ingestion.start()

    app = create_app(db=db, export_row_limit=config.export_row_limit)

    def _shutdown(_signum: int, _frame: object) -> None:
        logger.info("shutdown signal received")
        ingestion.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info("web UI listening on %s:%s", config.host, config.port)
    app.run(host=config.host, port=config.port, debug=False)
    ingestion.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
