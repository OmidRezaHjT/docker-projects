# Project 4 — CI/CD Pipeline with GitHub Actions and Docker Swarm

A small Flask app taken through a full delivery pipeline: automated tests and image builds on every push, a container registry, and a Docker Swarm stack with healthchecks, rolling updates, automatic rollback, Secrets and Configs.

## Pipeline

```
git push
   │
   ▼
GitHub Actions
   ├─ test   : pytest
   └─ build  : docker build → push to GHCR   (only if tests pass)
   │
   ▼
ghcr.io/omidrezahjt/cicd-app:<commit-sha>
   │
   ▼
docker stack deploy   (manual, one command)
   │
   ▼
Docker Swarm: 3 replicas, healthcheck, rolling update, auto-rollback
```

## Components

| Piece | Role |
|---|---|
| **Flask app** | Tiny service with `/` and `/health`; returns version, hostname and a greeting read from a Swarm Config |
| **pytest** | Quality gate: a failing test stops the pipeline before any image is built |
| **GitHub Actions** | Runs the tests and builds/pushes the image on every push |
| **GHCR** | GitHub's container registry; the image is tagged with the commit SHA |
| **registry:2** | Private registry used locally to learn `tag` / `push` / `pull` by hand |
| **Docker Swarm** | Runs the stack: replicas, self-healing, rolling updates, rollback |
| **Secrets / Configs** | Database password and app configuration kept out of the image and out of Git |

## Project structure

```
.github/workflows/
└── project4-ci.yml        # test → build → push to GHCR (repo root)
project4/
├── app/
│   ├── app.py
│   ├── test_app.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   └── .dockerignore
├── stack.yaml
└── README.md
```

## The image

Multi-stage `Dockerfile`:

- **builder** stage installs dependencies; the **final** stage copies only the result, so build leftovers are not shipped
- runs as a **non-root** user (`appuser`)
- `gunicorn` as the server, started in **exec form** (`CMD ["gunicorn", ...]`) so it receives `SIGTERM` directly and shuts down cleanly during rolling updates
- `requirements.txt` is copied before the code so the dependency layer is cached
- `pytest` lives in `requirements-dev.txt` and is not in the final image

## CI workflow

`.github/workflows/project4-ci.yml` has two jobs:

| Job | What it does |
|---|---|
| `test` | checkout → set up Python 3.12 → install dev requirements → `pytest -v` |
| `build` | `needs: test`; logs in to GHCR with the built-in `GITHUB_TOKEN`, builds the image and pushes it as `:<commit-sha>` and `:latest` |

Notes:

- `paths: project4/**` limits the workflow to changes in this project (the repo holds several)
- `permissions: packages: write` gives the job the minimum it needs to push
- images are tagged with the **commit SHA**, so you always know which code is running and can roll back to an exact version. `latest` is only a convenience and is not used for deployment

## Why two registries

I first ran a plain `registry:2` container locally (port 5050) and practiced `docker tag`, `push`, `pull` and listing tags through its API. The GitHub-hosted runner cannot reach `localhost`, so the pipeline pushes to **GHCR** instead. Swarm cannot `build:` either, so a registry is mandatory for deployment.

## Docker Swarm

Before writing the stack file I explored Swarm by hand:

```bash
docker swarm init
docker service create --name web --replicas 3 -p 5002:5000 <image>
docker service ps web
docker service scale web=5
docker service update --image <new-image> --update-parallelism 1 --update-delay 10s web
docker service rollback web
```

Things I verified:

- **Self-healing**: killing a container with `docker rm -f` makes Swarm create a replacement (the old task shows `exit 137`, i.e. `SIGKILL`)
- **Load balancing**: the routing mesh spreads requests across replicas; the app returns its hostname so this is visible with `curl`
- **Rolling update** with a `curl` loop running the whole time: no downtime, and both versions answer for a while
- **Rollback**: `docker service rollback web` returns to the previous version

## The stack (`stack.yaml`)

```bash
docker stack deploy --with-registry-auth -c stack.yaml cicd
```

| Setting | Why |
|---|---|
| `image:` only (no `build:`) | Swarm does not build; it pulls from a registry |
| `replicas: 3` | desired state; Swarm keeps reality equal to it |
| `healthcheck` | Swarm knows the app is *healthy*, not just running (the slim Python image has no `curl`, so the check uses Python) |
| `update_config.order: start-first` | the new task starts and becomes healthy before an old one is stopped |
| `update_config.failure_action: rollback` | a failed update is reverted automatically |
| `update_config.monitor: 30s` | watch each updated task long enough to notice failures (the 5 s default was too short) |
| `secrets` | Postgres password read from `/run/secrets/db_password` |
| `configs` | app configuration mounted at `/etc/app.conf` |
| `placement.constraints` | Postgres is pinned to one node (see limitations) |

`docker stack deploy` is used for both the first deployment and every update; Swarm applies only the difference.

### Secrets and Configs

```bash
printf 'S3cretPass!' | docker secret create db_password -
printf 'greeting=Hello from config v1\n' | docker config create app_conf_v1 -
```

| | Secret | Config |
|---|---|---|
| Use for | passwords, tokens | non-sensitive settings |
| Value visible in `inspect` | no | yes |
| Inside the container | `/run/secrets/<name>` (tmpfs) | any path, read-only |
| Changing it | create a new one with a new name | create a new one with a new name |

Both are immutable, so rotating means creating `app_conf_v2` and changing only the `name:` in `stack.yaml`, then deploying again. No image rebuild is needed.

Proof that the Secret is not leaked: `docker service inspect` shows only `POSTGRES_PASSWORD_FILE=/run/secrets/db_password`, while a plain `-e DB_PASSWORD=...` shows the password in clear text. The `web` service has no access to the Secret at all.

### Config vs Volume

A Config is something *I* write and the app only reads. A Volume is data the *app* writes and that must survive. Configs live inside Swarm and reach any node; a Volume lives on one node's disk.

## Demonstrations

**Automatic rollback.** I built a deliberately broken version whose `/health` returns 500 and deployed it. The new task never became healthy, the old tasks kept serving (thanks to `start-first`), and Swarm reported `rollback_completed`. A `curl` loop saw only the previous version, with no errors.

**Quality gate.** Because `build` depends on `test`, a failing test means no image is built or pushed.

## Limitations and decisions

- **Deploy is manual.** Fully automatic deployment needs a self-hosted runner on the machine that runs Swarm. I chose not to install one on my personal machine: a runner executes workflow code locally, which is risky on a public repository. The pipeline therefore ends with one manual `docker stack deploy`.
- **Single-node Swarm.** Manager quorum, overlay networking across nodes and node failure are not exercised.
- **Postgres uses a local volume pinned to one node.** In Swarm a volume exists only on the node where the task ran; if the task moved, it would silently start with an empty volume. Pinning avoids that, but the node is a single point of failure. A real setup needs backups, replication or shared storage.
- **`registry:2` has no authentication or TLS.** It is for local learning only.
- **Monitoring and logging are out of scope** here; they are covered in Projects 2 and 3.

## Troubleshooting notes

| Problem | Cause | Fix |
|---|---|---|
| Tasks `Rejected: failed to resolve reference` | image address used the wrong registry port | use the real port (`localhost:5050`), and check it with `curl <registry>/v2/_catalog` |
| `port is already allocated` | another container used the host port | change only the left side of `HOST:CONTAINER` |
| Healthcheck always failing | slim Python image has no `curl` | run the check with Python's `urllib` |
| Rollback did not trigger | default `monitor` period (5 s) was shorter than the time needed to detect failure | set `monitor: 30s` |
| YAML errors in `stack.yaml` | wrong indentation | two spaces per level, never tabs |
| CI failed on first run | `project4/` had not been pushed, so the workflow found no code | `git ls-files project4` before debugging the workflow |

## AI assistance

This project was built with the help of an AI assistant (Claude, by Anthropic), used to explain concepts, plan the roadmap and draft configuration. I ran, tested and debugged everything myself; the troubleshooting table above lists real problems I hit along the way.

## Possible next steps

- self-hosted runner (or SSH-based deploy) for fully automatic CD
- Nexus instead of `registry:2`, with authentication
- multi-node Swarm with shared storage for the database
- monitoring and logging as a separate project
