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

**Status:** ⏳ Planned

---

### Project 3 — DevOps CI/CD Pipeline

A production-style project focused on automating the application lifecycle.

Planned technologies:

* GitHub Actions
* Docker
* Docker Registry / Nexus
* Docker Swarm
* Secrets & Configs
* Deployment automation
* Monitoring & Logging

Expected workflow:

```text
Developer
   ↓
Git Push
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Build & Test
   ↓
Docker Image
   ↓
Registry
   ↓
Deployment
   ↓
Monitoring
```

**Status:** ⏳ Planned

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
│
└── project3/
```

## Purpose

This repository is part of my practical DevOps learning path.

Instead of only completing courses, the goal is to build, deploy, troubleshoot, document, and improve complete systems using industry-relevant tools and workflows.
