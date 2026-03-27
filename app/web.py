import csv
import io
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_file

from app.database import Database, ExportFilters


def _split_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts = []
    for chunk in raw.replace("\n", ",").split(","):
        value = chunk.strip()
        if value:
            parts.append(value)
    return parts


def _parse_filters() -> ExportFilters:
    source = request.form if request.method == "POST" else request.args
    return ExportFilters(
        start_time=(source.get("start_time") or None),
        end_time=(source.get("end_time") or None),
        include_domains=_split_list(source.get("include_domains")) or None,
        exclude_domains=_split_list(source.get("exclude_domains")) or None,
        include_entities=_split_list(source.get("include_entities")) or None,
        exclude_entities=_split_list(source.get("exclude_entities")) or None,
        include_areas=_split_list(source.get("include_areas")) or None,
        exclude_areas=_split_list(source.get("exclude_areas")) or None,
    )


def _render_home(metadata: dict[str, list[str]]) -> str:
    domains = "\n".join(metadata["domains"])
    entities = "\n".join(metadata["entities"])
    areas = "\n".join(metadata["areas"])
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>Home Assistant Data Dumper</title>
  <style>
    body {{ font-family: 'IBM Plex Sans', sans-serif; margin: 24px; background: linear-gradient(120deg,#f6f7fb,#e9f3ff); }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(240px, 1fr)); gap: 12px; }}
    label {{ display: flex; flex-direction: column; font-size: 13px; gap: 6px; }}
    textarea,input {{ border: 1px solid #b6c1d2; border-radius: 8px; padding: 8px; font-family: monospace; }}
    button {{ margin-top: 10px; margin-right: 10px; border: none; background: #0059b3; color: #fff; padding: 10px 14px; border-radius: 8px; }}
    .hint {{ color: #4f5d75; font-size: 12px; }}
    @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>Home Assistant Data Dumper</h1>
  <p class=\"hint\">Current UTC time: {now}</p>
  <form method=\"post\">
    <div class=\"grid\">
      <label>Start Time (ISO8601 UTC)
        <input name=\"start_time\" placeholder=\"2025-01-01T00:00:00Z\" />
      </label>
      <label>End Time (ISO8601 UTC)
        <input name=\"end_time\" placeholder=\"2026-01-01T00:00:00Z\" />
      </label>
      <label>Include Domains (comma/newline)
        <textarea rows=\"5\" name=\"include_domains\" placeholder=\"light,switch\"></textarea>
      </label>
      <label>Exclude Domains (comma/newline)
        <textarea rows=\"5\" name=\"exclude_domains\"></textarea>
      </label>
      <label>Include Entities (comma/newline)
        <textarea rows=\"5\" name=\"include_entities\" placeholder=\"light.kitchen\"></textarea>
      </label>
      <label>Exclude Entities (comma/newline)
        <textarea rows=\"5\" name=\"exclude_entities\"></textarea>
      </label>
      <label>Include Areas (comma/newline)
        <textarea rows=\"5\" name=\"include_areas\" placeholder=\"Kitchen\"></textarea>
      </label>
      <label>Exclude Areas (comma/newline)
        <textarea rows=\"5\" name=\"exclude_areas\"></textarea>
      </label>
    </div>
    <button formaction=\"/export/csv\" formmethod=\"post\">Export CSV</button>
    <button formaction=\"/export/db\" formmethod=\"post\">Export SQLite</button>
  </form>

  <h2>Known Domains</h2>
  <pre>{domains}</pre>
  <h2>Known Entities</h2>
  <pre>{entities}</pre>
  <h2>Known Areas</h2>
  <pre>{areas}</pre>
</body>
</html>"""


def create_app(db: Database, export_row_limit: int) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home() -> str:
        metadata = db.get_distinct_metadata()
        return _render_home(metadata)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/api/metadata")
    def metadata() -> Response:
        return jsonify(db.get_distinct_metadata())

    @app.route("/export/csv", methods=["GET", "POST"])
    def export_csv() -> Response:
        filters = _parse_filters()
        rows = db.fetch_events_for_export(filters, export_row_limit)

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "event_uid",
                "entity_id",
                "domain",
                "area_name",
                "changed_at",
                "old_state",
                "new_state",
                "transition_text",
                "explanation_text",
                "trigger_type",
                "trigger_entity_id",
                "automation_name",
                "source",
            ]
        )

        for row in rows:
            writer.writerow(
                [
                    row["event_uid"],
                    row["entity_id"],
                    row["domain"],
                    row["area_name"],
                    row["changed_at"],
                    row["old_state"],
                    row["new_state"],
                    row["transition_text"],
                    row["explanation_text"],
                    row["trigger_type"],
                    row["trigger_entity_id"],
                    row["automation_name"],
                    row["source"],
                ]
            )

        data = buffer.getvalue().encode("utf-8")
        filename = f"ha_data_export_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"

        return Response(
            data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @app.route("/export/db", methods=["GET", "POST"])
    def export_db() -> Response:
        filters = _parse_filters()
        temp_dir = tempfile.mkdtemp(prefix="ha_data_export_")
        temp_db = str(Path(temp_dir) / "filtered_export.sqlite3")

        count = db.clone_filtered_database(temp_db, filters, export_row_limit)
        if count == 0:
            Path(temp_db).unlink(missing_ok=True)
            os.rmdir(temp_dir)
            return Response("No rows matched the selected filters.", status=404)

        filename = f"ha_data_export_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.sqlite3"

        response = send_file(
            temp_db,
            mimetype="application/x-sqlite3",
            as_attachment=True,
            download_name=filename,
            max_age=0,
        )

        @response.call_on_close
        def _cleanup() -> None:
            Path(temp_db).unlink(missing_ok=True)
            Path(temp_dir).rmdir()

        return response

    return app
