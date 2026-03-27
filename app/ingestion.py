import hashlib
import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import Database
from app.ha_client import HomeAssistantClient, to_iso_z


def _parse_iso(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _transition_text(old_state: str | None, new_state: str | None) -> str:
    if old_state is None:
        return f"State initialized to {new_state}"
    return f"State changed from {old_state} to {new_state}"


class IngestionService:
    def __init__(
        self,
        db: Database,
        ha_client: HomeAssistantClient,
        poll_interval_seconds: int,
        history_chunk_hours: int,
    ) -> None:
        self.db = db
        self.ha_client = ha_client
        self.poll_interval_seconds = poll_interval_seconds
        self.history_chunk_hours = history_chunk_hours
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="ingestion", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=15)

    def _run(self) -> None:
        try:
            self._run_backfill_if_needed()
        except Exception:
            self.logger.exception("initial backfill failed")

        while not self._stop_event.is_set():
            try:
                self._run_poll_once()
            except Exception:
                self.logger.exception("poll loop failed")
            self._stop_event.wait(self.poll_interval_seconds)

    def _run_backfill_if_needed(self) -> None:
        if self.db.get_checkpoint("backfill_complete") == "1":
            return

        cursor_raw = self.db.get_checkpoint("backfill_cursor")
        if cursor_raw:
            cursor = _parse_iso(cursor_raw)
        else:
            cursor = datetime(1970, 1, 1, tzinfo=timezone.utc)

        self.logger.info("starting first-run backfill from %s", to_iso_z(cursor))

        chunk = timedelta(hours=self.history_chunk_hours)
        while not self._stop_event.is_set():
            now = datetime.now(timezone.utc)
            if cursor >= now:
                break

            window_end = min(cursor + chunk, now)
            self._process_window(cursor, window_end)
            self.db.set_checkpoint("backfill_cursor", to_iso_z(window_end))
            cursor = window_end

        if not self._stop_event.is_set():
            now = datetime.now(timezone.utc)
            self.db.set_checkpoint("backfill_complete", "1")
            self.db.set_checkpoint("last_poll_cursor", to_iso_z(now))
            self.logger.info("first-run backfill completed")

    def _run_poll_once(self) -> None:
        cursor_raw = self.db.get_checkpoint("last_poll_cursor")
        if cursor_raw:
            cursor = _parse_iso(cursor_raw)
        else:
            cursor = datetime.now(timezone.utc) - timedelta(seconds=max(self.poll_interval_seconds * 2, 60))

        now = datetime.now(timezone.utc)
        self._process_window(cursor, now)
        self.db.set_checkpoint("last_poll_cursor", to_iso_z(now))

    def _process_window(self, start_time: datetime, end_time: datetime) -> None:
        if end_time <= start_time:
            return

        history = self.ha_client.fetch_history(start_time, end_time)
        logbook = self.ha_client.fetch_logbook(start_time, end_time)
        explanations = self._build_explanation_index(logbook)

        inserted = 0
        for event in history:
            explanation = self._pick_explanation(explanations, event)
            if self._persist_event(event, explanation):
                inserted += 1

        self.logger.info(
            "ingestion window %s -> %s processed=%d inserted=%d",
            to_iso_z(start_time),
            to_iso_z(end_time),
            len(history),
            inserted,
        )

    @staticmethod
    def _build_explanation_index(logbook: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        index: dict[str, list[dict[str, Any]]] = {}
        for row in logbook:
            entity_id = row.get("entity_id")
            when_raw = row.get("when")
            if not entity_id or not when_raw:
                continue

            try:
                when = _parse_iso(when_raw)
            except ValueError:
                continue

            explanation = {
                "when": when,
                "explanation_text": row.get("message") or row.get("name") or "",
                "trigger_type": row.get("source"),
                "trigger_entity_id": row.get("entity_id"),
                "automation_name": row.get("name"),
                "source": row.get("source"),
            }
            index.setdefault(entity_id, []).append(explanation)

        for values in index.values():
            values.sort(key=lambda item: item["when"])

        return index

    @staticmethod
    def _pick_explanation(index: dict[str, list[dict[str, Any]]], event: dict[str, Any]) -> dict[str, Any] | None:
        entity_rows = index.get(event["entity_id"], [])
        if not entity_rows:
            return None

        changed_at = event["changed_at"]
        nearest: dict[str, Any] | None = None
        nearest_delta = timedelta(days=3650)

        for row in entity_rows:
            delta = abs(row["when"] - changed_at)
            if delta < nearest_delta:
                nearest = row
                nearest_delta = delta

        if nearest is None or nearest_delta > timedelta(seconds=60):
            return None

        return {
            "explanation_text": nearest.get("explanation_text", ""),
            "trigger_type": nearest.get("trigger_type"),
            "trigger_entity_id": nearest.get("trigger_entity_id"),
            "automation_name": nearest.get("automation_name"),
            "source": nearest.get("source"),
        }

    def _persist_event(self, event: dict[str, Any], explanation: dict[str, Any] | None) -> bool:
        changed_at_iso = to_iso_z(event["changed_at"])
        context_id = event.get("context", {}).get("id")
        uid_seed = "|".join(
            [
                event["entity_id"],
                changed_at_iso,
                str(event.get("new_state")),
                str(context_id),
            ]
        )
        event_uid = hashlib.sha256(uid_seed.encode("utf-8")).hexdigest()

        area_name = None
        attributes = event.get("attributes", {})
        if isinstance(attributes, dict):
            area_name = attributes.get("area_name")
            if area_name is None:
                area_name = attributes.get("area")

        return self.db.upsert_event(
            event_uid=event_uid,
            entity_id=event["entity_id"],
            domain=event["domain"],
            area_name=str(area_name) if area_name else None,
            changed_at=changed_at_iso,
            old_state=event.get("old_state"),
            new_state=event.get("new_state"),
            transition_text=_transition_text(event.get("old_state"), event.get("new_state")),
            value_payload=event.get("raw", {}),
            attributes_payload=attributes if isinstance(attributes, dict) else None,
            explanation=explanation,
        )
