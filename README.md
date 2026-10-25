# Docker & DevOps Projects

A hands-on project series focused on building practical Docker and DevOps skills through real-world application scenarios.

The goal of this repository is to move beyond tutorials and practice containerization, networking, persistent storage, observability, and CI/CD by building complete projects from scratch.

## Projects

### Project 1 — Multi-Container Application

A multi-container application built with:

* Nginx
* Flask Backend
* PostgreSQL
* Docker Network
* Persistent Volume
* Docker Compose

Architecture:

```text
Client
   ↓
Nginx :80
   ↓
Flask Backend :5000
   ↓
PostgreSQL :5432
   ↓
Persistent Volume
```

The project is first built manually with Docker commands and then reproduced using Docker Compose.

**Status:** ✅ Completed

---

### Project 2 — Observability Stack

A containerized application with monitoring and logging.

Planned technologies:

* Docker
* Docker Compose
* Prometheus
* Grafana
* Logging / ELK components

The goal is to monitor application and infrastructure metrics and gain practical experience with centralized observability.

**Status:** ✅ Completed

---

### Project 3 — Centralized Logging with ELK Stack

A centralized logging pipeline for collecting, parsing, and searching logs across multiple containerized services.

Planned technologies:

* Elasticsearch
* Logstash
* Kibana
* Filebeat
* Docker Compose

The goal is to collect logs from services (e.g. Nginx, Flask, PostgreSQL), parse and structure them, and build searchable dashboards — separate from metrics-based monitoring.

**Status:** ✅ Completed

---

## Project 4 — DevOps CI/CD Pipeline

A CI/CD pipeline for a small Flask app: automated tests and image builds on every push, a container registry, and a Docker Swarm stack with healthchecks, rolling updates, automatic rollback, Secrets and Configs.

Built with:

* GitHub Actions
* Docker (multi-stage build)
* GitHub Container Registry (GHCR) and a local `registry:2`
* Docker Swarm
* Secrets & Configs
* pytest

Workflow:

```
Developer
   ↓
Git Push
   ↓
GitHub Actions
   ↓
Test (pytest)
   ↓
Build Docker Image
   ↓
Push to GHCR (tagged with commit SHA)
   ↓
Deploy to Docker Swarm (docker stack deploy)
   ↓
Healthcheck, rolling update, automatic rollback
```

Highlights:

* Image build and push only run if the tests pass
* Zero-downtime rolling updates, verified with a continuous `curl` loop
* Deliberately broken release (failing `/health`) was rolled back automatically by Swarm
* Database password stored as a Docker Secret, app settings as a Docker Config (changed without rebuilding the image)

Notes:

* Deployment is a manual `docker stack deploy`; a self-hosted runner was intentionally not used on a personal machine
* Monitoring and logging are covered in Projects 2 and 3

**Status:** ✅ Completed
---

## Learning Goals

Through these projects, I am focusing on:

* Docker containerization
* Docker networking
* Persistent storage
* Docker Compose
* Reverse Proxy
* Application deployment
* Monitoring and observability
* Logging
* CI/CD
* Container registries
* Docker Swarm
* Secrets and configuration management
* Practical DevOps workflows

## Technologies

```text
Linux
Docker
Docker Compose
Nginx
Python / Flask
PostgreSQL
Prometheus
Grafana
ELK
Git
GitHub Actions
Nexus
Docker Swarm
```

## Repository Structure

```text
docker-projects/
│
├── project1/
│   ├── backend/
│   ├── nginx/
│   └── compose.yml
│
├── project2/
│   ├── backend/
│   ├── grafana/
│   ├── logstash/
│   ├── prometheus/
│   └── compose.yml
│
├── project3/
│   ├── filebeat/
│   ├── flask-app/
│   ├── logstash/
│   ├── nginx/
│   ├── README.md
│   └── compose.yml
│
└── project4/
│   ├── app/
│   ├── README.md
│   ├── stack.yaml

```

## Purpose

This repository is part of my practical DevOps learning path.

Instead of only completing courses, the goal is to build, deploy, troubleshoot, document, and improve complete systems using industry-relevant tools and workflows.
