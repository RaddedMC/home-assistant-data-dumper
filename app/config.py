import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    db_path: str
    host: str
    port: int
    poll_interval_seconds: int
    history_chunk_hours: int
    export_row_limit: int
    log_level: str
    ha_api_base: str
    supervisor_token: str


DEFAULT_OPTIONS_PATH = "/data/options.json"


def _as_int(value: object, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_config(options_path: str = DEFAULT_OPTIONS_PATH) -> AppConfig:
    options: dict = {}
    path = Path(options_path)
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            options = json.load(handle)

    return AppConfig(
        db_path=os.getenv("DATA_DUMPER_DB", "/data/data_dumper.sqlite3"),
        host=os.getenv("DATA_DUMPER_HOST", "0.0.0.0"),
        port=_as_int(os.getenv("DATA_DUMPER_PORT", "8067"), 8067),
        poll_interval_seconds=_as_int(options.get("poll_interval_seconds"), 30),
        history_chunk_hours=_as_int(options.get("history_chunk_hours"), 24),
        export_row_limit=_as_int(options.get("export_row_limit"), 500000),
        log_level=str(options.get("log_level", "info")).upper(),
        ha_api_base=os.getenv("HA_API_BASE", "http://supervisor/core/api"),
        supervisor_token=os.getenv("SUPERVISOR_TOKEN", ""),
    )
