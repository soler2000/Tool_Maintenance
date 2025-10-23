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

Follow the steps below to bring the FastAPI backend up on a development workstation or a
Raspberry Pi running Raspberry Pi OS (Debian Bookworm). The commands assume a Unix-like
shell (Linux/macOS). On Windows, run the same commands inside PowerShell with the
`python`/`pip` executables that ship with your Python 3.11 installation.

1. **Install system packages**

   Raspberry Pi OS Bookworm already ships Python 3.11 as its default interpreter, so the
   generic packages are sufficient:

   ```bash
   sudo apt-get update
   sudo apt-get install -y git python3 python3-venv python3-pip
   ```

   On other Debian/Ubuntu hosts you can replace `python3` with `python3.11` if that
   package is available; otherwise the generic packages still deliver Python 3.11.

2. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Tool_Maintenance
   ```

3. **Create and activate a virtual environment**

   The backend’s dependencies include `uvicorn[standard]`, `SQLAlchemy`, and other
   packages that should remain isolated from the system interpreter:

   ```bash
   python3 -m venv backend/.venv
   source backend/.venv/bin/activate
   ```

   After activation your shell prompt should be prefixed with `(.venv)`.

4. **Upgrade `pip` and install the backend package**

   Run the editable install from the `backend` directory so the dependencies declared in
   `backend/pyproject.toml` (including `uvicorn`) are pulled into the virtual environment.

   ```bash
   cd backend
   python -m pip install --upgrade pip
   python -m pip install -e .
   python -m pip show uvicorn  # optional sanity check
   ```

   If the installer ever reports `does not appear to be a Python project`, double-check
   that the command was executed from inside the `backend` folder or uses the explicit
   `python -m pip install -e ./backend` path from the repository root.

5. **Run the development server**

   With the virtual environment still active, start Uvicorn via the module entry point.
   Using `python -m uvicorn` ensures the interpreter finds the dependency inside the
   virtual environment even if the console script is not on `PATH`.

   ```bash
   python -m uvicorn app.main:app --reload --port 6000
   ```

6. **Open the interactive API documentation**

   Visit `http://127.0.0.1:6000/docs` once Uvicorn reports that it is running. The Swagger
   UI exposes user registration, authentication, and the full set of CRUD endpoints for
   tools, shot counters, maintenance logs, failures, and action items.

7. **(Optional) Configure environment overrides**

   Environment variables (see `backend/app/config.py`) can be defined in a `.env` file to
   override defaults such as the database connection string, JWT secret, and CORS
   settings. Create `backend/.env` and export variables in `KEY=value` format when needed.

## Next Steps
1. Extend the backend with background workers for scheduled maintenance reminders and reporting.
2. Build the React-based frontend client described in `docs/architecture.md`.
3. Integrate photo capture/upload workflow and storage management.
4. Implement analytics dashboards and automated maintenance alerts.

