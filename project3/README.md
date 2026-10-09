# Project 3 — Centralized Logging with the ELK Stack

A centralized logging pipeline that collects, parses, stores and visualizes logs from three different containerized services, each with a different log format.

## Architecture

```
Nginx (text)      ─┐
Flask (JSON)      ─┼─►  Filebeat  ──►  Logstash  ──►  Elasticsearch  ──►  Kibana
PostgreSQL (text) ─┘    (collect)      (parse)          (store/index)      (visualize)
```

Each service writes its log to a file on a shared named volume. Filebeat tails those files, tags every event with a `service` field, and ships them to Logstash on port 5044. Logstash applies a per-service filter and routes each event to its own daily index.

## Components

| Tool | Role in this project |
|---|---|
| **Elasticsearch** | Stores and indexes logs as JSON documents |
| **Logstash** | Parses raw log lines into structured fields (`grok`, `json`, `date`) |
| **Kibana** | Search UI and dashboards |
| **Filebeat** | Lightweight shipper: reads log files and forwards them to Logstash |
| **Nginx** | Log source, plain-text access log |
| **Flask** | Log source, writes one JSON object per request |
| **PostgreSQL** | Log source, plain-text server log with statements and errors |

## Project structure

```
project3/
├── compose.yml
├── flask-app/
│   ├── app.py
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── filebeat/
│   └── filebeat.yml
├── logstash/
│   └── pipeline/
│       └── logstash.conf
└── README.md
```

## Run

```bash
docker compose up -d --build
docker compose ps -a
```

| Service | URL |
|---|---|
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |
| Nginx | http://localhost:8080 |
| Flask | http://localhost:5001 |

### Generate some logs

```bash
curl http://localhost:8080
curl http://localhost:8080/not-found
curl http://localhost:5001/health
docker exec postgres psql -U appuser -d appdb -c "SELECT 1;"
docker exec postgres psql -U appuser -d appdb -c "SELECT * FROM missing_table;"
```

### Verify

```bash
curl "http://localhost:9200/_cat/indices?v" | grep logs
curl "http://localhost:9200/postgres-logs-*/_search?pretty" -H "Content-Type: application/json" \
  -d '{"query": {"match": {"pg_level": "ERROR"}}}'
```

Then in Kibana create Data Views for `nginx-logs-*`, `flask-logs-*`, `postgres-logs-*` and explore them in Discover.

## How each source is parsed

| Service | Format | Logstash filter |
|---|---|---|
| Nginx | Combined access log (plain text) | `grok` with the built-in `COMBINEDAPACHELOG` pattern |
| Flask | JSON, written by the app itself | `json` (no pattern needed) |
| PostgreSQL | Plain text, own format | `grok` with a **custom pattern** |

Custom pattern for PostgreSQL:

```
%{TIMESTAMP_ISO8601:pg_time} %{WORD:pg_tz} \[%{NUMBER:pg_pid}\] %{WORD:pg_level}:\s+%{GREEDYDATA:pg_message}
```

Every source also goes through a `date` filter so that `@timestamp` reflects when the event happened, not when it was processed.

Rule of thumb learned here: if you control the application, log JSON from the start; use `grok` only for software whose format you cannot change.

## Key design decisions

- **Filebeat in front of Logstash.** Filebeat is lightweight and built for collection; Logstash is heavy and built for processing.
- **Routing by a `service` field** added in `filebeat.yml` (`fields` + `fields_under_root`), with conditionals in both the `filter` and `output` sections of Logstash.
- **One index per service per day**, e.g. `nginx-logs-2026.10.09`.
- **Named volumes for data shared between containers** (`es_data`, `nginx_logs`, `flask_logs`, `postgres_logs`, `postgres_data`, `filebeat_data`). **Bind mounts for files I edit by hand** (all config files, mounted read-only).
- **Read-only mounts (`:ro`)** for any container that only needs to read logs.
- **`filebeat_data` volume** keeps Filebeat's registry, so it does not re-send old lines after a container is recreated.

## Troubleshooting notes

Problems hit while building this, and what fixed them:

| Problem | Cause | Fix |
|---|---|---|
| Logstash: `Unsupported or unrecognized SSL message` | Output used `https://` while ES security is disabled | Use `http://elasticsearch:9200` |
| `docker attach` stopped the container | `Ctrl+C` is forwarded to the main process | Detach with `Ctrl+P` then `Ctrl+Q` |
| Port mapping not applied | Container was only restarted | `docker compose up -d --force-recreate <service>` |
| Nginx wrote nothing to the log file | `access.log` is a symlink to `/dev/stdout` in the official image, and a new named volume copies it | Log to a new filename (`custom_access.log`) |
| Filebeat: `must be owned by uid=0 or root` | Bind-mounted config owned by the host user | Fix ownership and run with `user: root` |
| Filebeat: `no path is configured` | Typos: `path`/`field` instead of `paths`/`fields` | Fix keys; check the `keys present on the config` startup log line |
| No `service` field, no index created | Same typo (`field:`); events silently matched no `output` condition | Fix key, recreate Filebeat |
| Flask port 5000 already allocated | Another project's container used it | Map `5001:5000` |
| Logstash `ConfigurationError` at top level | A block fell outside `filter { }` (misplaced `}`) | Fix braces; keep every `if` inside `filter` / `output` |
| `DELETE` with wildcard rejected | `action.destructive_requires_name` defaults to true | Delete indices by exact name |
| Kibana Discover empty | Time range did not cover the data | Widen the time range |

Debugging order that worked every time: check the source file, then Filebeat logs, then Logstash logs, then query Elasticsearch directly with `curl`, and only then look at Kibana.

## Notes

- This setup is for local learning. Elasticsearch security is disabled and the PostgreSQL credentials are plain text in `compose.yml`.
- `log_statement=all` makes PostgreSQL log every query; useful for demos, too verbose for production.
- Filebeat runs as root to read files owned by other containers' users.

## AI Assistance

This project was built with the help of an AI assistant (Claude). I used it to explain the tools, plan the roadmap, and draft configuration files step by step. I ran, tested and debugged everything myself, and the troubleshooting section above lists real problems I hit along the way.

