# Lot Traceability System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat)
![Alembic](https://img.shields.io/badge/Alembic-1.16-6BA81E?style=flat)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-tested-0A9EDC?style=flat&logo=pytest&logoColor=white)

A full-stack web application for tracking manufacturing lots through their pre-sterilization lifecycle in an FDA/ISO-regulated medical device manufacturing environment. Built with FastAPI, PostgreSQL, and a vanilla JavaScript frontend with a role-based multi-user interface.

**🔗 Live demo:** [lot-traceability-system.up.railway.app](https://lot-traceability-system.up.railway.app)

> The demo runs on a free tier that may sleep after inactivity. The first request may take 30–60 seconds to wake the service.

---

## Overview

In sterile medical device manufacturing, every production lot must be traceable through each stage of its lifecycle for quality control and regulatory compliance. This system models the **pre-sterilization** stage of that traceability: a lot enters the system when it is ready for audit, is reviewed by a quality auditor, and is then either **released** (authorized to proceed to sterilization) or placed on **hold**.

The domain model draws on real-world experience in FDA/ISO-regulated medical device manufacturing, which shapes the business rules, the audit workflow, the disposition review process, and the role structure.

---

## Features

### Lot lifecycle
- **Create lots** — register a new lot with lot ID, part number, units, and manufacturing date.
- **Audit workflow** — an auditor signs in with their credentials to take a lot into the audit process; their name auto-populates from their profile.
- **Disposition review** — a dedicated review screen presents lot data and auditor information alongside a quality checklist before the auditor releases or holds the lot.
- **Hold workflow** — placing a lot on hold requires an NCR number. Returning a lot from hold requires dual signatures: one Quality Engineer and one Manufacturing lead, each entering their own credentials. The system tracks who has signed and shows who is still pending (`waiting_qe_approval` / `waiting_me_approval`).
- **State-aware UI** — action buttons appear only when business rules permit. Invalid operations are blocked at the API level and hidden at the UI level.

### Catalog management
- **Product families** — proposed by Manufacturing Engineers, approved by Quality Engineers before becoming active.
- **Part numbers** — same dual-approval flow; only active part numbers appear in the lot creation dropdown.
- **Descriptions are tied to part numbers** — not entered manually per lot, ensuring consistency.

### Role-based access

| Role | Capabilities |
|---|---|
| `admin` | Create and manage users, activate/deactivate accounts, change roles |
| `engineer` | Propose and approve product families and part numbers, create lots, co-sign hold returns |
| `manufacturing` | Create lots, co-sign hold returns |
| `auditor` | Audit lots (credential-verified), disposition lots |

### Interface
- Sidebar navigation with role-filtered menu items
- Dashboard with live metrics and activity feed
- Active Lots table with search, family/status filters, and pagination
- History table with date range filters and CSV/PDF export
- Audits view grouped by inspector
- Reports: daily summary and historical breakdown by part number
- Lot detail slide-in panel with contextual actions
- Dark mode (default) and light mode toggle, persisted in localStorage

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Data validation | Pydantic |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT (python-jose + passlib/bcrypt) |
| Database | PostgreSQL (production) / SQLite (local development) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Testing | pytest |
| Deployment | Railway |

---

## Data model

### Status flow

```
ready_for_audit
       │
in_audit_process
       │
    ┌──┴──┐
released  hold
              │
   waiting_qe_approval  ← ME signed, QE pending
   waiting_me_approval  ← QE signed, ME pending
              │
       ready_for_audit
```

### Business rules

- A lot ID can appear across multiple batches as long as the part number differs — the unique constraint is on `(lot_id, part_number_code)`.
- A lot can only be audited from `ready_for_audit` (409 otherwise).
- A lot can only be dispositioned from `in_audit_process` (409 otherwise).
- Placing a lot on hold requires an NCR number.
- Returning a lot from hold requires one QE Engineer signature and one Manufacturing signature; either can sign first.
- Part numbers and product families require ME proposal and QE approval before becoming active.
- Only active part numbers appear in the lot creation form.
- Inactive users cannot log in.

---

## API endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Authenticate and receive a JWT token |
| `GET` | `/auth/me` | Return the current user's profile |

### Users (admin only)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/` | List all users |
| `POST` | `/users/` | Create a new user |
| `PATCH` | `/users/{username}/toggle-active` | Activate or deactivate a user |
| `PATCH` | `/users/{username}/role` | Change a user's role |

### Product Families
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/product-families/` | List all families |
| `GET` | `/product-families/active` | List active families only |
| `POST` | `/product-families/` | Propose a new family (engineer only) |
| `PATCH` | `/product-families/{name}/approve` | Approve a pending family (engineer only) |

### Part Numbers
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/part-numbers/` | List all part numbers |
| `GET` | `/part-numbers/active` | List active part numbers only |
| `POST` | `/part-numbers/` | Propose a new part number (engineer only) |
| `PATCH` | `/part-numbers/{code}/approve` | Approve a pending part number (engineer only) |

### Lots
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/lots/` | List all lots |
| `GET` | `/lots/{batch_id}` | Get a single lot |
| `POST` | `/lots/` | Create a new lot (manufacturing / engineer) |
| `PATCH` | `/lots/{batch_id}/audit` | Start audit with auditor credentials |
| `PATCH` | `/lots/{batch_id}/disposition` | Release or hold a lot (auditor) |
| `PATCH` | `/lots/{batch_id}/return-from-hold` | Sign a hold return (engineer / manufacturing) |

---

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

# Apply migrations
alembic upgrade head

# Seed the database with demo data (optional)
python seed_database.py

# Run the development server
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser. Locally the app uses SQLite — no database setup required.

### Demo credentials (after seeding)

All demo users share the password: `Password123!`

| Username | Role |
|---|---|
| `john.miller` | admin |
| `michael.carter` | engineer |
| `david.thompson` | engineer |
| `james.wilson` | manufacturing |
| `robert.anderson` | manufacturing |
| `william.johnson` | auditor |
| `daniel.brown` | auditor |
| `jennifer.davis` | auditor |

---

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (local) |
| `SECRET_KEY` | JWT signing secret | `dev-secret-key-change-in-production` |

---

## Testing

```bash
python -m pytest -v
```

Tests run against an in-memory SQLite database with dependency overrides, isolated from the development database.

---

## Project structure

```
lot-traceability-system/
├── app/
│   ├── main.py              # App startup and router mounting
│   ├── database.py          # SQLAlchemy engine and session
│   ├── auth/
│   │   ├── dependencies.py  # JWT verification and role guards
│   │   ├── router.py        # /auth endpoints
│   │   └── security.py      # Password hashing and token creation
│   ├── models/
│   │   ├── db_models.py     # SQLAlchemy ORM models
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── routers/
│   │   ├── lots.py
│   │   ├── part_numbers.py
│   │   ├── product_families.py
│   │   └── users.py
│   └── services/
│       ├── lot_service.py
│       ├── part_number_service.py
│       ├── product_family_service.py
│       └── user_service.py
├── alembic/                 # Database migrations
├── static/                  # Frontend (HTML, CSS, JS)
├── tests/
│   └── test_lots.py
├── seed_database.py         # Demo data seed script
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Author

**Gerardo Gutiérrez**
[LinkedIn](https://www.linkedin.com/in/gerardo-gutierrez91) · [GitHub](https://github.com/ernestog-cmd)
