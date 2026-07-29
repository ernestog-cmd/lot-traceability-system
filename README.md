# Lot Traceability System

A backend system for tracking manufacturing lots through their pre-sterilization lifecycle in a regulated (FDA/ISO) manufacturing environment. Built with FastAPI.

## Domain Context

In sterile medical device manufacturing, each production lot must be traceable through every stage of its lifecycle for compliance and quality control. This system models that traceability: lots are received, audited, and either released or held based on the audit outcome.

## Version 1 Scope (Pre-Sterilization)

The current version models the **pre-sterilization** stage: a lot is created, goes through a single audit, and is then released (authorized to ship it to sterilization process) or placed on hold.

### Lot Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique lot identifier |
| `part_number` | string | Product part number |
| `description` | string | Product description |
| `product_family` | string | Product family (drapes, instruments, cannulas, needles, etc.) |
| `units` | integer | Number of units in the lot |
| `manufacturing_date` | date | Manufacturing date |
| `status` | enum | Lot lifecycle status |
| `audited_by` | string (optional) | Auditor who reviewed the lot |
| `audited_at` | datetime (optional) | Timestamp of the audit |

### Lot Status Flow

received -> in_audit -> released / hold

## Roadmap (Version 2 - Post-Sterilization)

- Second audit stage performed by Post-Sterilization Quality Assurance team
- Additional process dates: sterilization dispatch, Arrival at the distribution center, post-audit disposition
- Post-sterilization status states
- Manufacturing location tracking

## Tech Stack

- **FastAPI** - API framework
- **Pydantic** - data validation
- **PostgreSQL** - persistence (in progress)
- **SQLAlchemy** - ORM (in progress)