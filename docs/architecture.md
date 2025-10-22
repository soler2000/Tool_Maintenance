# System Architecture Blueprint

This document outlines the proposed architecture for the Tool Maintenance Management System designed to run on a Raspberry Pi while remaining scalable to multiple facilities.

## Overview
The solution follows a modular service-oriented architecture packaged via Docker Compose. Each component is lightweight to accommodate Raspberry Pi hardware constraints while supporting future horizontal scaling.

## Components
### 1. Web Frontend
- Technology: React + TypeScript using Vite build system.
- Responsibilities: responsive UI, offline-aware forms for maintenance logs, photo capture via WebRTC, dashboard visualisations (Chart.js or ECharts).
- Deployment: served as static assets through Nginx; communicates with backend API via HTTPS.

### 2. API Gateway & Backend Services
- Technology: Python FastAPI application.
- Responsibilities:
  - Authentication (JWT-based) and role-based authorisation.
  - CRUD endpoints for tools, shot counts, maintenance logs, failure codes, failure reports, photos, and action items.
  - File upload endpoints streaming photos to object storage.
  - Report generation endpoints returning JSON/CSV exports.
- Deployment: Gunicorn/Uvicorn workers behind Nginx reverse proxy.

### 3. Database Layer
- PostgreSQL 15 running in a container with TimescaleDB extension for time-series shot counts.
- Features:
  - Row-level security policies to restrict data visibility by site.
  - Logical backups via nightly `pg_dump` and WAL archiving to network storage.

### 4. Object Storage
- MinIO container storing images and future documents.
- Configured with lifecycle policies to tier older photos to cheaper storage if integrated with cloud.

### 5. Background Workers
- Celery workers with Redis broker for asynchronous tasks:
  - Resize/compress uploaded images.
  - Generate scheduled PDF reports (WeasyPrint) for management reviews.
  - Send email/SMS notifications for overdue actions or high-severity failures.

### 6. Edge Integrations
- OPC-UA client microservice polling injection moulding machine counters.
- MQTT listener for capturing condition monitoring sensor data.
- Data forwarded to API via secure service account credentials.

## Data Flow
1. Technician logs in via web UI using Pi-hosted URL.
2. Technician records maintenance log or failure report; forms call FastAPI endpoints.
3. API writes transactional data to PostgreSQL and streams images to MinIO.
4. Background workers process images and schedule follow-up actions.
5. Dashboards query aggregated views from PostgreSQL for real-time insights.

## Security Controls
- HTTPS termination at Nginx using Let's Encrypt certificates.
- OAuth2-compatible authentication enabling SSO with plant Active Directory (future enhancement).
- Periodic vulnerability scanning of containers using Trivy.
- Automated user session timeout and multi-factor authentication support for admin roles.

## Deployment Pipeline
- GitHub repository with GitHub Actions CI/CD.
- CI steps: linting (ESLint, Ruff), unit tests, integration tests with Docker Compose.
- CD: Build multi-arch Docker images (linux/amd64 + linux/arm64) and push to private registry. Pi pulls latest images via watchtower or Ansible playbooks.

## Monitoring & Observability
- Prometheus + Grafana stack for metrics (CPU, memory, API latency, shot count ingestion).
- Loki for log aggregation with fluent-bit shipping container logs.
- Health-check endpoints for readiness/liveness; alerts configured via Alertmanager.

## Offline & Resilience Strategy
- Local caching for forms using IndexedDB to tolerate temporary network loss.
- Graceful degradation: allow manual photo uploads if camera offline.
- Scheduled system self-check verifying storage space, database connectivity, and camera availability.

## Future Enhancements
- Predictive maintenance models using captured data (TensorFlow Lite on Pi or cloud inference).
- Integration with ERP/MES for tool availability and production scheduling.
- Mobile app wrapper using Capacitor for dedicated handheld devices.

