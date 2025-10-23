# Data Model Overview

The Tool Maintenance Management System stores structured information about tooling assets, maintenance activities, failures, and follow-up actions. The following schema outlines the core entities and relationships for an MVP implementation.

## Entity Relationships
```
Tool 1---* ToolShotCounter
Tool 1---* MaintenanceLog *---1 User
Tool 1---* FailureReport *---* FailureCode
FailureReport 1---* FailurePhoto
Tool 1---* ToolPhoto
Tool 1---* ActionItem *---1 User (assignee)
```

## Entities
### Tool
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary identifier |
| asset_number | String (unique) | Shop floor asset ID |
| name | String | Tool name or part number |
| description | Text | Free-form description |
| manufacturer | String | Optional |
| cavity_count | Integer | Optional |
| status | Enum(`active`, `maintenance`, `retired`) | Lifecycle state |
| location | String | Storage rack or press assignment |
| created_at / updated_at | Timestamp | Audit trail |

### ToolShotCounter
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary identifier |
| tool_id | UUID (FK Tool) | |
| shot_count | Integer | Incremental total |
| recorded_by | UUID (FK User) | |
| source | Enum(`manual`, `imported`, `automatic`) | Data origin |
| recorded_at | Timestamp | |

### MaintenanceLog
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| tool_id | UUID (FK Tool) | |
| performed_by | UUID (FK User) | Technician |
| checklist_template | UUID (FK ChecklistTemplate) | Optional |
| performed_at | Timestamp | |
| duration_minutes | Integer | Optional |
| observations | Text | |
| follow_up_required | Boolean | |

### FailureCode
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| code | String | Short identifier (e.g., `FL-001`) |
| name | String | Failure category |
| description | Text | Detailed explanation |
| severity_default | Enum(`low`, `medium`, `high`) | Default severity |
| active | Boolean | Allows retiring codes |

### FailureReport
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| tool_id | UUID (FK Tool) | |
| reported_by | UUID (FK User) | |
| failure_code_id | UUID (FK FailureCode) | Reference failure taxonomy |
| severity | Enum(`low`, `medium`, `high`, `critical`) | Overrides default |
| description | Text | Observations |
| occurred_at | Timestamp | |
| containment_action | Text | Immediate steps taken |

### FailurePhoto
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| failure_report_id | UUID (FK FailureReport) | |
| storage_path | String | File system or S3 key |
| caption | String | Optional |
| captured_at | Timestamp | Defaults to upload time |

### ToolPhoto
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| tool_id | UUID (FK Tool) | |
| storage_path | String | |
| angle | Enum(`front`, `rear`, `core`, `cavity`, `other`) | Optional |
| captured_at | Timestamp | |

### ActionItem
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| tool_id | UUID (FK Tool) | |
| failure_report_id | UUID (FK FailureReport) | Optional link |
| title | String | |
| description | Text | |
| assigned_to | UUID (FK User) | Responsible owner |
| due_date | Date | |
| status | Enum(`open`, `in_progress`, `completed`, `cancelled`) | |
| completed_at | Timestamp | Optional |

### User
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| username | String (unique) | |
| full_name | String | |
| email | String | Optional |
| role | Enum(`technician`, `engineer`, `manager`, `admin`) | Governs permissions |
| password_hash | String | |
| created_at / last_login_at | Timestamp | |

### ChecklistTemplate (Optional Extension)
| Field | Type | Notes |
| --- | --- | --- |
| id | UUID | |
| name | String | |
| description | Text | |
| steps | JSONB | Ordered list of inspection steps |
| active | Boolean | |

## Audit & Integration Tables
- **AuditLog:** Stores user actions (entity type, entity id, action, timestamp, metadata JSON payload).
- **IntegrationEvent:** Records inbound PLC/OPC-UA messages for shot counts with raw payload and processing status.

## File Storage Strategy
- Store images under `/data/tool_photos/{tool_id}/{uuid}.jpg` by default.
- Generate thumbnail derivatives for faster UI rendering.
- Retain EXIF metadata to preserve capture timestamps.

## Reporting Views
- Materialised views for metrics such as `tool_utilisation`, `failure_frequency`, and `action_overdue` to power dashboards efficiently.

