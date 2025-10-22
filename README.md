# Tool Maintenance Management System

A web-based tooling maintenance program designed for Raspberry Pi deployments to manage injection moulding tools. The application enables technicians and engineers to register tooling assets, record post-production maintenance, and track performance trends.

## Objectives
- Maintain an accurate inventory of tooling assets and associated metadata.
- Record best-practice post-run maintenance activities and inspection findings.
- Track shot counts for each tool to support preventative maintenance scheduling.
- Capture structured failure reports from a curated list of potential tooling issues.
- Attach photographic evidence for tools and observed defects.
- Assign and monitor follow-up actions to ensure timely resolution of issues.

## Target Environment
- **Hardware:** Raspberry Pi 4 Model B (4GB or higher recommended) with camera module or USB camera for capturing tool photos.
- **Operating System:** Raspberry Pi OS (64-bit) with Docker or Python 3.11 runtime.
- **Network:** Local facility network with secure Wi-Fi or Ethernet connectivity; optional remote VPN access.

## High-Level Architecture
1. **Frontend Web Client** (React or Vue) served via Nginx or a lightweight Node.js server on the Raspberry Pi. Provides responsive UI for tablets/kiosks on the shop floor.
2. **Backend API** (FastAPI / Flask) handling user authentication, business logic, and integrations.
3. **Database** (PostgreSQL or SQLite for single-node deployments) storing asset records, maintenance logs, defect reports, and action items.
4. **Object Storage** (local filesystem or S3-compatible service such as MinIO) for storing tool and defect photographs.
5. **Background Workers** (Celery/RQ) for scheduled maintenance reminders, report generation, and photo processing.

## Core Modules
- **Tool Registry:** Create, update, and retire tool records with metadata (asset number, cavity count, manufacturer, etc.).
- **Shot Count Tracker:** Update counts manually or via OPC-UA/PLC integrations; enforce thresholds for maintenance reminders.
- **Inspection & Maintenance Logs:** Record post-run inspections, cleaning tasks, lubrication, and spare part replacements referencing best practices.
- **Failure Reporting:** Select standardized failure codes from a configurable catalog; capture severity, affected components, and root-cause analysis.
- **Photo Management:** Upload and annotate images of tools and defects; support camera capture on Raspberry Pi.
- **Action Management:** Assign corrective actions to users, define due dates, track completion, and link to relevant failures.
- **Analytics & Reporting:** Generate dashboards for tool utilisation, failure trends, maintenance compliance, and outstanding actions.

## Data Protection & Security
- Role-based access control differentiating technicians, engineers, and administrators.
- Encrypted data at rest (database & image storage) and TLS for all network traffic.
- Audit logs capturing user edits, deletions, and photo uploads.
- Configurable data retention policies aligned with regulatory requirements.

## Deployment Considerations
- Use Docker Compose to orchestrate services (API, frontend, database, object storage, worker, and reverse proxy).
- Integrate Pi-specific optimisations: GPU acceleration for image processing, hardware watchdog, and read-only filesystem overlays for resilience.
- Schedule nightly backups to network storage; include database dump and image archive.

## Backend Implementation

The repository now includes a FastAPI backend located in `backend/app` that realises the
core workflows described in the foundational documentation. Key capabilities include:

- JWT-based authentication with user registration and token issuance endpoints.
- CRUD APIs for tools, shot counters, maintenance logs, failure codes/reports, and action items.
- SQLAlchemy models aligned with the schema defined in `docs/data_model.md`.
- Async SQLite persistence by default (configurable via environment variables).

### Local Development

1. Ensure Python 3.11+ is installed.
2. Install dependencies using the provided `pyproject.toml`:

   ```bash
   cd backend
   pip install -e .
   ```

3. Launch the API with Uvicorn:

   ```bash
   uvicorn app.main:app --reload --port 6000
   ```

4. Access the interactive API docs at `http://127.0.0.1:6000/docs`.

Environment variables (see `backend/app/config.py`) can be defined in a `.env` file to
override defaults such as the database connection string, JWT secret, and CORS settings.

## Next Steps
1. Extend the backend with background workers for scheduled maintenance reminders and reporting.
2. Build the React-based frontend client described in `docs/architecture.md`.
3. Integrate photo capture/upload workflow and storage management.
4. Implement analytics dashboards and automated maintenance alerts.

