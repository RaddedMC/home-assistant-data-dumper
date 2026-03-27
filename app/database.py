import json
import re
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExportFilters:
    start_time: str | None = None
    end_time: str | None = None
    include_domains: list[str] | None = None
    exclude_domains: list[str] | None = None
    include_entities: list[str] | None = None
    exclude_entities: list[str] | None = None
    include_areas: list[str] | None = None
    exclude_areas: list[str] | None = None


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self._lock, self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_uid TEXT UNIQUE NOT NULL,
                    entity_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    area_name TEXT,
                    changed_at TEXT NOT NULL,
                    old_state TEXT,
                    new_state TEXT,
                    transition_text TEXT
                );

                CREATE TABLE IF NOT EXISTS event_explanations (
                    event_id INTEGER PRIMARY KEY,
                    explanation_text TEXT NOT NULL,
                    trigger_type TEXT,
                    trigger_entity_id TEXT,
                    automation_name TEXT,
                    source TEXT,
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_changed_at ON events(changed_at);
                CREATE INDEX IF NOT EXISTS idx_events_entity_time ON events(entity_id, changed_at);
                CREATE INDEX IF NOT EXISTS idx_events_area ON events(area_name);
                CREATE INDEX IF NOT EXISTS idx_events_domain ON events(domain);
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO schema_version(version, applied_at) VALUES (1, datetime('now'))"
            )
            conn.commit()

    @staticmethod
    def _domain_table_name(domain: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", domain.strip().lower())
        return f"domain_{safe}_values"

    def ensure_domain_table(self, domain: str) -> str:
        table = self._domain_table_name(domain)
        with self._lock, self.connect() as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER UNIQUE NOT NULL,
                    state TEXT,
                    value_json TEXT NOT NULL,
                    attributes_json TEXT,
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_event_id ON {table}(event_id)"
            )
            conn.commit()
        return table

    def set_checkpoint(self, key: str, value: str) -> None:
        with self._lock, self.connect() as conn:
            conn.execute(
                """
                INSERT INTO checkpoints(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (key, value),
            )
            conn.commit()

    def get_checkpoint(self, key: str) -> str | None:
        with self._lock, self.connect() as conn:
            row = conn.execute("SELECT value FROM checkpoints WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def upsert_event(
        self,
        event_uid: str,
        entity_id: str,
        domain: str,
        area_name: str | None,
        changed_at: str,
        old_state: str | None,
        new_state: str | None,
        transition_text: str | None,
        value_payload: dict[str, Any],
        attributes_payload: dict[str, Any] | None,
        explanation: dict[str, Any] | None,
    ) -> bool:
        table = self.ensure_domain_table(domain)
        with self._lock, self.connect() as conn:
            conn.execute("BEGIN")
            existing = conn.execute(
                "SELECT id FROM events WHERE event_uid = ?", (event_uid,)
            ).fetchone()
            if existing:
                conn.execute("ROLLBACK")
                return False

            cursor = conn.execute(
                """
                INSERT INTO events(
                    event_uid, entity_id, domain, area_name, changed_at,
                    old_state, new_state, transition_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_uid,
                    entity_id,
                    domain,
                    area_name,
                    changed_at,
                    old_state,
                    new_state,
                    transition_text,
                ),
            )
            event_id = cursor.lastrowid

            conn.execute(
                f"""
                INSERT OR REPLACE INTO {table}(event_id, state, value_json, attributes_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event_id,
                    new_state,
                    json.dumps(value_payload, separators=(",", ":")),
                    json.dumps(attributes_payload, separators=(",", ":")) if attributes_payload is not None else None,
                ),
            )

            if explanation:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO event_explanations(
                        event_id, explanation_text, trigger_type,
                        trigger_entity_id, automation_name, source
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        explanation.get("explanation_text", ""),
                        explanation.get("trigger_type"),
                        explanation.get("trigger_entity_id"),
                        explanation.get("automation_name"),
                        explanation.get("source"),
                    ),
                )

            conn.execute("COMMIT")
            return True

    def get_distinct_metadata(self) -> dict[str, list[str]]:
        with self._lock, self.connect() as conn:
            domains = [row[0] for row in conn.execute("SELECT DISTINCT domain FROM events ORDER BY domain").fetchall()]
            entities = [row[0] for row in conn.execute("SELECT DISTINCT entity_id FROM events ORDER BY entity_id").fetchall()]
            areas = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT area_name FROM events WHERE area_name IS NOT NULL AND area_name != '' ORDER BY area_name"
                ).fetchall()
            ]
        return {"domains": domains, "entities": entities, "areas": areas}

    @staticmethod
    def _list_filter_clause(column: str, include: list[str] | None, exclude: list[str] | None) -> tuple[list[str], list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if include:
            placeholders = ",".join("?" for _ in include)
            clauses.append(f"{column} IN ({placeholders})")
            params.extend(include)
        if exclude:
            placeholders = ",".join("?" for _ in exclude)
            clauses.append(f"{column} NOT IN ({placeholders})")
            params.extend(exclude)
        return clauses, params

    def _build_filter_sql(self, filters: ExportFilters) -> tuple[str, list[Any]]:
        clauses = []
        params: list[Any] = []

        if filters.start_time:
            clauses.append("e.changed_at >= ?")
            params.append(filters.start_time)
        if filters.end_time:
            clauses.append("e.changed_at <= ?")
            params.append(filters.end_time)

        for column, include, exclude in (
            ("e.domain", filters.include_domains, filters.exclude_domains),
            ("e.entity_id", filters.include_entities, filters.exclude_entities),
            ("e.area_name", filters.include_areas, filters.exclude_areas),
        ):
            partial_clauses, partial_params = self._list_filter_clause(column, include, exclude)
            clauses.extend(partial_clauses)
            params.extend(partial_params)

        where_sql = ""
        if clauses:
            where_sql = "WHERE " + " AND ".join(clauses)
        return where_sql, params

    def fetch_events_for_export(self, filters: ExportFilters, limit: int) -> list[dict[str, Any]]:
        where_sql, params = self._build_filter_sql(filters)
        query = f"""
            SELECT
                e.id,
                e.event_uid,
                e.entity_id,
                e.domain,
                e.area_name,
                e.changed_at,
                e.old_state,
                e.new_state,
                e.transition_text,
                x.explanation_text,
                x.trigger_type,
                x.trigger_entity_id,
                x.automation_name,
                x.source
            FROM events e
            LEFT JOIN event_explanations x ON x.event_id = e.id
            {where_sql}
            ORDER BY e.changed_at ASC
            LIMIT ?
        """
        params.append(limit)
        with self._lock, self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def clone_filtered_database(self, target_path: str, filters: ExportFilters, limit: int) -> int:
        target = Database(target_path)
        target.initialize()

        events = self.fetch_events_for_export(filters, limit)
        if not events:
            return 0

        event_ids = [row["id"] for row in events]
        domains = sorted({row["domain"] for row in events})

        domain_tables = {domain: target.ensure_domain_table(domain) for domain in domains}

        with target._lock, target.connect() as conn:
            conn.execute("BEGIN")
            for row in events:
                conn.execute(
                    """
                    INSERT INTO events(
                        id, event_uid, entity_id, domain, area_name, changed_at,
                        old_state, new_state, transition_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["event_uid"],
                        row["entity_id"],
                        row["domain"],
                        row["area_name"],
                        row["changed_at"],
                        row["old_state"],
                        row["new_state"],
                        row["transition_text"],
                    ),
                )

                if row["explanation_text"]:
                    conn.execute(
                        """
                        INSERT INTO event_explanations(
                            event_id, explanation_text, trigger_type,
                            trigger_entity_id, automation_name, source
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["id"],
                            row["explanation_text"],
                            row["trigger_type"],
                            row["trigger_entity_id"],
                            row["automation_name"],
                            row["source"],
                        ),
                    )

            id_placeholders = ",".join("?" for _ in event_ids)
            source_conn = self.connect()
            try:
                for domain in domains:
                    table = domain_tables[domain]
                    source_rows = source_conn.execute(
                        f"SELECT event_id, state, value_json, attributes_json FROM {table} WHERE event_id IN ({id_placeholders})",
                        event_ids,
                    ).fetchall()
                    for source_row in source_rows:
                        conn.execute(
                            f"""
                            INSERT INTO {table}(event_id, state, value_json, attributes_json)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                source_row["event_id"],
                                source_row["state"],
                                source_row["value_json"],
                                source_row["attributes_json"],
                            ),
                        )
            finally:
                source_conn.close()

            conn.execute("COMMIT")

        return len(events)
