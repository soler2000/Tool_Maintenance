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

## Next Steps
1. Finalize technology stack selections and document them in `docs/architecture.md`.
2. Define API contracts and database schema (see `docs/data_model.md`).
3. Implement authentication and role management.
4. Develop CRUD interfaces for tools, failures, maintenance logs, and actions.
5. Integrate photo capture/upload workflow and storage management.
6. Create analytics dashboards and automated maintenance alerts.

