# Lot Traceability System

A backend system for tracking manufacturing lots through their pre-sterilization lifecycle in a regulated (FDA/ISO) manufacturing environment. Built with FastAPI.

## Domain Context

In sterile medical device manufacturing, each production lot must be traceable through every stage of its lifecycle for compliance and quality control. This system models that traceability: lots enter the system when they are ready for audit, are reviewed by a quality auditor, and are either released (authorized to ship to the sterilization process) or placed on hold.

Manufacturing itself happens outside this system's scope. A lot enters the domain only once it is ready for audit; manufacturing dates are stored as traceability data, not as a tracked stage.

## Version 1 Scope (Pre-Sterilization)

The current version models the **pre-sterilization** stage: a lot enters ready for audit, goes through a single audit, and is then released or placed on hold.

### Lot Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique lot identifier |
| `part_number` | string | Product part number |
| `description` | string | Product description |
| `product_family` | string | Product family (drapes, instruments, cannulas, needles, etc.) |
| `units` | integer | Number of units in the lot |
| `manufacturing_date` | date | Manufacturing date (traceability data) |
| `status` | enum | Lot lifecycle status |
| `audited_by` | Auditor (optional) | Auditor who reviewed the lot |
| `audited_at` | datetime (optional) | Timestamp of the audit |

### Auditor Model

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | Auditor's first name (display) |
| `last_name` | string | Auditor's last name (display) |
| `system_user` | string | Unique system username (identifier) |

### Lot Status Flow

ready_for_audit -> in_audit_process -> released / hold

### Business Rules

- A lot enters the system in `ready_for_audit`.
- When a lot moves to `in_audit_process`, `audited_by` and `audited_at` become required.
- `system_user` uniquely identifies an auditor; legal names may repeat across homonyms, the system username never does.

## Roadmap (Version 2 - Post-Sterilization)

- Second audit stage performed by the Post-Sterilization Quality Assurance team
- Additional process dates: sterilization dispatch, arrival at the distribution center, post-audit disposition
- Post-sterilization status states (including `received` upon sterilized return to the DC)
- Manufacturing location tracking
- Automatic `system_user` generation (first-name initial + last name, numeric suffix for homonyms)

## Tech Stack

- **FastAPI** - API framework
- **Pydantic** - data validation
- **PostgreSQL** - persistence (in progress)
- **SQLAlchemy** - ORM (in progress)