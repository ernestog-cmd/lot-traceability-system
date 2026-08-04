# Lot Traceability System

A full-stack web application for tracking manufacturing lots through their pre-sterilization lifecycle in a regulated (FDA/ISO) medical device manufacturing environment. Built with FastAPI, PostgreSQL, and a vanilla JavaScript frontend, deployed as a live public service.

**🔗 Live demo:** [lot-traceability-system.onrender.com](https://lot-traceability-system.onrender.com)

> Note: the demo is hosted on a free tier that sleeps after inactivity. The first request may take ~30–60 seconds to wake the service; subsequent requests are immediate.

---

## Overview

In sterile medical device manufacturing, every production lot must be traceable through each stage of its lifecycle for quality control and regulatory compliance. This system models the **pre-sterilization** stage of that traceability: a lot enters the system when it is ready for audit, is reviewed by a quality auditor, and is then either **released** (authorized to proceed to sterilization) or placed on **hold**.

The domain model was designed drawing on real-world experience in FDA/ISO-regulated medical device manufacturing, which shapes the business rules, the audit workflow, and the disposition review process.

## Domain scope

Manufacturing itself happens **outside** this system's scope. A lot enters the domain only once it is ready for audit; the manufacturing date is stored as traceability data, not as a tracked stage. The current version covers the pre-sterilization workflow end to end: a lot enters `ready_for_audit`, an auditor is assigned (moving it to `in_audit_process`), and a disposition review results in `released` or `hold`.

## Features

- **Create lots** — register a new lot with part number, description, product family, units, and manufacturing date.
- **Audit workflow** — assign an auditor to a lot, moving it into the audit process. Audit actions are only available on lots in a valid state.
- **Disposition review** — a dedicated review screen presents lot data and auditor information side by side, along with a quality checklist (no physical damage, quantity matches system, work order audited, correct WIP location), before the auditor releases or holds the lot.
- **State-aware UI** — action buttons appear only when the business rules permit them. A lot that cannot be audited or dispositioned simply offers no such action, so the interface guides the user and prevents invalid operations.
- **Active vs. history views** — lots that require action are shown in an "Active Lots" table; resolved lots (released or hold) move to a "History" table, ordered most-recent-first with a show-more control.
- **Color-coded statuses** — each lifecycle status carries a distinct color so state is readable at a glance.

## Tech stack

| Layer | Technology |
|-------|-----------|
| API framework | FastAPI |
| Data validation | Pydantic |
| ORM | SQLAlchemy |
| Database | PostgreSQL (production) / SQLite (local development) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Testing | pytest |
| Deployment | Render |

The database layer is environment-driven: the same codebase runs on SQLite locally and PostgreSQL in production by reading the connection string from an environment variable, so no code changes are needed between environments.

## Data model

### Lot

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique lot identifier (primary key) |
| `part_number` | string | Product part number |
| `description` | string | Product description |
| `product_family` | string | Product family (instruments, drapes, needles, etc.) |
| `units` | integer | Number of units in the lot |
| `manufacturing_date` | date | Manufacturing date (traceability data) |
| `status` | enum | Lot lifecycle status |
| `audited_by` | Auditor (optional) | Auditor who reviewed the lot |
| `audited_at` | datetime (optional) | Timestamp of the audit |

### Auditor

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | Auditor's first name (display) |
| `last_name` | string | Auditor's last name (display) |
| `system_user` | string | Unique system username (identifier) |

### Status flow

```
ready_for_audit  ->  in_audit_process  ->  released
                                       \-> hold
```

### Business rules

- A lot enters the system in `ready_for_audit`.
- A lot can only be audited from `ready_for_audit` (otherwise the API returns `409 Conflict`).
- A lot can only be dispositioned from `in_audit_process` (otherwise `409 Conflict`).
- An auditor is mandatory when auditing; `audited_by` and `audited_at` are set at that point.
- `system_user` uniquely identifies an auditor. Legal names may repeat across homonyms; the system username never does.
- Lot `id` is unique; attempting to create a duplicate returns a descriptive error.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web interface |
| `GET` | `/lots` | List all lots |
| `GET` | `/lots/{lot_id}` | Get a single lot (404 if not found) |
| `POST` | `/lots` | Create a new lot |
| `PATCH` | `/lots/{lot_id}/audit` | Assign an auditor and start the audit process |
| `PATCH` | `/lots/{lot_id}/disposition?decision=released\|hold` | Release or hold a lot |

## Testing

The project includes an automated test suite (pytest) covering both the happy path and error cases:

- Root endpoint serves the interface
- Lot creation
- Full lifecycle (create → audit → dispose)
- Auditing a non-existent lot returns `404`
- Auditing an already-audited lot returns `409`
- Dispositioning a lot that has not been audited returns `409`

Tests run against an in-memory SQLite database with dependency overrides, so they are fast and isolated from the development database.

```bash
python -m pytest -v
```

## Running locally

```bash
# Clone the repository
git clone https://github.com/ernestog-cmd/lot-traceability-system.git
cd lot-traceability-system

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` in your browser. Locally the app uses SQLite; no database setup is required.

## Roadmap

The project is designed to evolve across versions, with each version laying the groundwork for the next.

### Version 2 — Data model & architecture

Refinements planned to support a richer domain and enable the timeline features of v3:

- **State history table** — record every status transition (old status, new status, changed by, timestamp) so a lot's full timeline can be reconstructed, rather than storing only the current status.
- **Normalized auditor** — move the auditor into its own related table referenced by foreign key, instead of flattened columns on the lot.
- **Disposition as an entity** — store each disposition (decision, reviewer, timestamp, comments) as its own record.
- **Persisted checklist** — model review criteria as data (`ChecklistItem` + per-lot `LotChecklist`), so the criteria applied to each audit are recorded rather than being visual-only.
- **Automatic timestamps** — `created_at`, `updated_at`, and `disposed_at` maintained automatically.
- **Automatic `system_user` generation** — first-initial + last name, with a numeric suffix for homonyms.
- **React frontend** — migrate the interface to a component-based frontend.

### Version 2 — Domain expansion (post-sterilization)

- Second audit stage performed by the Post-Sterilization Quality Assurance team
- Additional process dates: sterilization dispatch, arrival at the distribution center, post-audit disposition
- Post-sterilization status states (including `received` upon sterilized return to the DC)
- Manufacturing location tracking

### Version 3 — Operations dashboard

- Metric cards (active, in audit, on hold, released)
- Per-lot progress timeline with real transition dates (enabled by the v2 state history table)
- Recent activity feed
- Search, filtering, and reporting

---

## Author

**Gerardo Gutiérrez**
[LinkedIn](https://www.linkedin.com/in/gerardo-gutierrez91) · [GitHub](https://github.com/ernestog-cmd)