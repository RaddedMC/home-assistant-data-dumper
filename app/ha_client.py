import logging
from datetime import datetime, timezone
from typing import Any

import requests


def _parse_ha_time(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class HomeAssistantClient:
    def __init__(self, api_base: str, token: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.logger = logging.getLogger(__name__)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self.session.get(
            f"{self.api_base}{path}",
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def fetch_history(self, start_time: datetime, end_time: datetime) -> list[dict[str, Any]]:
        params = {
            "end_time": to_iso_z(end_time),
            "minimal_response": "true",
            "significant_changes_only": "false",
            "no_attributes": "false",
        }

        try:
            response = self._get(f"/history/period/{to_iso_z(start_time)}", params=params)
        except requests.RequestException as exc:
            self.logger.warning("history fetch failed: %s", exc)
            return []

        events: list[dict[str, Any]] = []
        for entity_series in response:
            if not entity_series:
                continue

            previous_state: str | None = None
            for row in entity_series:
                entity_id = row.get("entity_id")
                if not entity_id:
                    continue

                changed_at = _parse_ha_time(row.get("last_changed") or row.get("last_updated"))
                if not changed_at:
                    continue

                state = str(row.get("state")) if row.get("state") is not None else None
                attributes = row.get("attributes") if isinstance(row.get("attributes"), dict) else {}
                context = row.get("context") if isinstance(row.get("context"), dict) else {}

                events.append(
                    {
                        "entity_id": entity_id,
                        "domain": entity_id.split(".", 1)[0],
                        "changed_at": changed_at,
                        "old_state": previous_state,
                        "new_state": state,
                        "attributes": attributes,
                        "context": context,
                        "raw": row,
                    }
                )
                previous_state = state

        events.sort(key=lambda item: (item["changed_at"], item["entity_id"]))
        return events

    def fetch_logbook(self, start_time: datetime, end_time: datetime) -> list[dict[str, Any]]:
        params = {
            "start_time": to_iso_z(start_time),
            "end_time": to_iso_z(end_time),
        }

        try:
            response = self._get("/logbook", params=params)
        except requests.RequestException as exc:
            self.logger.warning("logbook fetch failed: %s", exc)
            return []

        if not isinstance(response, list):
            return []
        return [entry for entry in response if isinstance(entry, dict)]
