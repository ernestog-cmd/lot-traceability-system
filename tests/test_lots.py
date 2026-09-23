import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.auth.security import hash_password
from app.models.db_models import UserDB, ProductFamily, PartNumber

# ============================================================
# ENGINE Y SESIÓN DE PRUEBA
# ============================================================

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture()
def seed_catalog(db):
    """Crea los usuarios, familia y part number mínimos para las pruebas."""

    users = [
        UserDB(username="admin",        hashed_password=hash_password("pass"), first_name="Admin",    last_name="System",   role="admin",         is_active="true"),
        UserDB(username="qe.engineer",  hashed_password=hash_password("pass"), first_name="Michael",  last_name="Carter",   role="engineer",      is_active="true"),
        UserDB(username="me.lead",      hashed_password=hash_password("pass"), first_name="James",    last_name="Wilson",   role="manufacturing", is_active="true"),
        UserDB(username="auditor1",     hashed_password=hash_password("pass"), first_name="William",  last_name="Johnson",  role="auditor",       is_active="true"),
        UserDB(username="inactive.user",hashed_password=hash_password("pass"), first_name="Inactive", last_name="User",     role="auditor",       is_active="false"),
    ]
    for u in users:
        db.add(u)

    family = ProductFamily(
        name="EndoWrist Instruments",
        status="active",
        proposed_by="qe.engineer",
        approved_by="qe.engineer",
    )
    db.add(family)

    part = PartNumber(
        code="470179",
        description="Monopolar curved scissors",
        family_name="EndoWrist Instruments",
        status="active",
        proposed_by="qe.engineer",
        approved_by="qe.engineer",
    )
    db.add(part)

    db.commit()


def login(username: str, password: str = "pass") -> str:
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


def auth(username: str) -> dict:
    return {"Authorization": f"Bearer {login(username)}"}


# ============================================================
# AUTH
# ============================================================

class TestAuth:

    def test_login_correct_credentials(self, seed_catalog):
        response = client.post(
            "/auth/login",
            data={"username": "auditor1", "password": "pass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, seed_catalog):
        response = client.post(
            "/auth/login",
            data={"username": "auditor1", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, seed_catalog):
        response = client.post(
            "/auth/login",
            data={"username": "inactive.user", "password": "pass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 403

    def test_get_me(self, seed_catalog):
        response = client.get("/auth/me", headers=auth("auditor1"))
        assert response.status_code == 200
        assert response.json()["username"] == "auditor1"
        assert response.json()["role"] == "auditor"

    def test_protected_route_without_token(self, seed_catalog):
        response = client.get("/users/")
        assert response.status_code == 401

    def test_wrong_role_blocked(self, seed_catalog):
        # auditor no puede ver /users/
        response = client.get("/users/", headers=auth("auditor1"))
        assert response.status_code == 403


# ============================================================
# USERS
# ============================================================

class TestUsers:

    def test_admin_can_list_users(self, seed_catalog):
        response = client.get("/users/", headers=auth("admin"))
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_admin_can_create_user(self, seed_catalog):
        response = client.post("/users/", headers=auth("admin"), json={
            "username": "new.user",
            "password": "pass",
            "first_name": "New",
            "last_name": "User",
            "role": "auditor",
        })
        assert response.status_code == 201
        assert response.json()["username"] == "new.user"

    def test_duplicate_username_fails(self, seed_catalog):
        response = client.post("/users/", headers=auth("admin"), json={
            "username": "auditor1",
            "password": "pass",
            "first_name": "Another",
            "last_name": "User",
            "role": "auditor",
        })
        assert response.status_code == 409

    def test_toggle_active(self, seed_catalog):
        response = client.patch(
            "/users/auditor1/toggle-active", headers=auth("admin")
        )
        assert response.status_code == 200
        assert response.json()["is_active"] == "false"

    def test_change_role(self, seed_catalog):
        response = client.patch(
            "/users/auditor1/role",
            headers=auth("admin"),
            json={"role": "manufacturing"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "manufacturing"


# ============================================================
# PRODUCT FAMILIES
# ============================================================

class TestProductFamilies:

    def test_engineer_can_propose_family(self, seed_catalog):
        response = client.post(
            "/product-families/",
            headers=auth("qe.engineer"),
            json={"name": "Vision Equipment"},
        )
        assert response.status_code == 201
        assert response.json()["status"] == "pending_qe_approval"

    def test_non_engineer_cannot_propose_family(self, seed_catalog):
        response = client.post(
            "/product-families/",
            headers=auth("auditor1"),
            json={"name": "Vision Equipment"},
        )
        assert response.status_code == 403

    def test_approve_family(self, seed_catalog):
        client.post(
            "/product-families/",
            headers=auth("qe.engineer"),
            json={"name": "Vision Equipment"},
        )
        response = client.patch(
            "/product-families/Vision Equipment/approve",
            headers=auth("qe.engineer"),
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_duplicate_family_fails(self, seed_catalog):
        response = client.post(
            "/product-families/",
            headers=auth("qe.engineer"),
            json={"name": "EndoWrist Instruments"},
        )
        assert response.status_code == 409


# ============================================================
# PART NUMBERS
# ============================================================

class TestPartNumbers:

    def test_engineer_can_propose_part_number(self, seed_catalog):
        response = client.post(
            "/part-numbers/",
            headers=auth("qe.engineer"),
            json={
                "code": "471172",
                "description": "Maryland bipolar forceps",
                "family_name": "EndoWrist Instruments",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "pending_qe_approval"

    def test_non_engineer_cannot_propose_part_number(self, seed_catalog):
        response = client.post(
            "/part-numbers/",
            headers=auth("me.lead"),
            json={
                "code": "471172",
                "description": "Maryland bipolar forceps",
                "family_name": "EndoWrist Instruments",
            },
        )
        assert response.status_code == 403

    def test_part_number_inactive_family_fails(self, seed_catalog):
        # Familia pendiente — no activa
        client.post(
            "/product-families/",
            headers=auth("qe.engineer"),
            json={"name": "Pending Family"},
        )
        response = client.post(
            "/part-numbers/",
            headers=auth("qe.engineer"),
            json={
                "code": "999999",
                "description": "Test",
                "family_name": "Pending Family",
            },
        )
        assert response.status_code == 404

    def test_active_part_numbers_endpoint(self, seed_catalog):
        response = client.get("/part-numbers/active")
        assert response.status_code == 200
        codes = [pn["code"] for pn in response.json()]
        assert "470179" in codes


# ============================================================
# LOTS — CREACIÓN
# ============================================================

class TestLotCreation:

    def test_manufacturing_can_create_lot(self, seed_catalog):
        response = client.post(
            "/lots/",
            headers=auth("me.lead"),
            json={
                "lot_id": "LOT-001",
                "part_number_code": "470179",
                "units": 100,
                "manufacturing_date": "2026-09-01",
                "status": "ready_for_audit",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["lot_id"] == "LOT-001"
        assert body["status"] == "ready_for_audit"
        assert body["part_number_description"] == "Monopolar curved scissors"

    def test_auditor_cannot_create_lot(self, seed_catalog):
        response = client.post(
            "/lots/",
            headers=auth("auditor1"),
            json={
                "lot_id": "LOT-002",
                "part_number_code": "470179",
                "units": 50,
                "manufacturing_date": "2026-09-01",
                "status": "ready_for_audit",
            },
        )
        assert response.status_code == 403

    def test_duplicate_lot_part_number_fails(self, seed_catalog):
        payload = {
            "lot_id": "LOT-001",
            "part_number_code": "470179",
            "units": 100,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        }
        client.post("/lots/", headers=auth("me.lead"), json=payload)
        response = client.post("/lots/", headers=auth("me.lead"), json=payload)
        assert response.status_code == 409

    def test_same_lot_id_different_part_number_allowed(self, seed_catalog):
        # Agregar segundo PN activo
        db = TestingSessionLocal()
        db.add(PartNumber(
            code="471172",
            description="Maryland bipolar forceps",
            family_name="EndoWrist Instruments",
            status="active",
            proposed_by="qe.engineer",
            approved_by="qe.engineer",
        ))
        db.commit()
        db.close()

        r1 = client.post("/lots/", headers=auth("me.lead"), json={
            "lot_id": "LOT-SHARED",
            "part_number_code": "470179",
            "units": 100,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        })
        r2 = client.post("/lots/", headers=auth("me.lead"), json={
            "lot_id": "LOT-SHARED",
            "part_number_code": "471172",
            "units": 80,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        })
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_inactive_part_number_fails(self, seed_catalog):
        db = TestingSessionLocal()
        db.add(PartNumber(
            code="999000",
            description="Inactive PN",
            family_name="EndoWrist Instruments",
            status="pending_qe_approval",
            proposed_by="qe.engineer",
        ))
        db.commit()
        db.close()

        response = client.post("/lots/", headers=auth("me.lead"), json={
            "lot_id": "LOT-BAD",
            "part_number_code": "999000",
            "units": 10,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        })
        assert response.status_code == 404


# ============================================================
# LOTS — FLUJO COMPLETO
# ============================================================

class TestLotLifecycle:

    def _create_lot(self, lot_id="LOT-TEST"):
        return client.post("/lots/", headers=auth("me.lead"), json={
            "lot_id": lot_id,
            "part_number_code": "470179",
            "units": 100,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        }).json()["batch_id"]

    def test_full_lifecycle_released(self, seed_catalog):
        batch_id = self._create_lot()

        audit = client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1",
            "password": "pass",
        })
        assert audit.status_code == 200
        assert audit.json()["status"] == "in_audit_process"
        assert audit.json()["audited_by"]["system_user"] == "auditor1"
        assert audit.json()["audited_by"]["first_name"] == "William"

        disposition = client.patch(
            f"/lots/{batch_id}/disposition",
            headers=auth("auditor1"),
            json={"decision": "released"},
        )
        assert disposition.status_code == 200
        assert disposition.json()["status"] == "released"

    def test_full_lifecycle_hold(self, seed_catalog):
        batch_id = self._create_lot("LOT-HOLD")

        client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "pass"
        })

        disposition = client.patch(
            f"/lots/{batch_id}/disposition",
            headers=auth("auditor1"),
            json={"decision": "hold", "ncr_number": "NCR-2026-0001"},
        )
        assert disposition.status_code == 200
        assert disposition.json()["status"] == "hold"
        assert disposition.json()["ncr_number"] == "NCR-2026-0001"

    def test_hold_without_ncr_fails(self, seed_catalog):
        batch_id = self._create_lot("LOT-NCR")
        client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "pass"
        })
        response = client.patch(
            f"/lots/{batch_id}/disposition",
            headers=auth("auditor1"),
            json={"decision": "hold"},
        )
        assert response.status_code == 422

    def test_audit_nonexistent_lot(self, seed_catalog):
        response = client.patch("/lots/9999/audit", json={
            "username": "auditor1", "password": "pass"
        })
        assert response.status_code == 404

    def test_audit_wrong_credentials(self, seed_catalog):
        batch_id = self._create_lot()
        response = client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "wrong"
        })
        assert response.status_code == 401

    def test_non_auditor_cannot_audit(self, seed_catalog):
        batch_id = self._create_lot()
        response = client.patch(f"/lots/{batch_id}/audit", json={
            "username": "me.lead", "password": "pass"
        })
        assert response.status_code == 403

    def test_audit_already_in_audit_fails(self, seed_catalog):
        batch_id = self._create_lot()
        client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "pass"
        })
        response = client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "pass"
        })
        assert response.status_code == 409

    def test_dispose_without_audit_fails(self, seed_catalog):
        batch_id = self._create_lot()
        response = client.patch(
            f"/lots/{batch_id}/disposition",
            headers=auth("auditor1"),
            json={"decision": "released"},
        )
        assert response.status_code == 409


# ============================================================
# LOTS — RETURN FROM HOLD (DOBLE FIRMA)
# ============================================================

class TestReturnFromHold:

    def _lot_on_hold(self) -> int:
        batch_id = client.post("/lots/", headers=auth("me.lead"), json={
            "lot_id": "LOT-HOLD-FLOW",
            "part_number_code": "470179",
            "units": 50,
            "manufacturing_date": "2026-09-01",
            "status": "ready_for_audit",
        }).json()["batch_id"]

        client.patch(f"/lots/{batch_id}/audit", json={
            "username": "auditor1", "password": "pass"
        })
        client.patch(
            f"/lots/{batch_id}/disposition",
            headers=auth("auditor1"),
            json={"decision": "hold", "ncr_number": "NCR-0001"},
        )
        return batch_id

    def test_qe_signs_first_then_me(self, seed_catalog):
        batch_id = self._lot_on_hold()

        r1 = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "qe.engineer", "password": "pass"
        })
        assert r1.status_code == 200
        assert r1.json()["status"] == "waiting_me_approval"

        r2 = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "me.lead", "password": "pass"
        })
        assert r2.status_code == 200
        assert r2.json()["status"] == "ready_for_audit"

    def test_me_signs_first_then_qe(self, seed_catalog):
        batch_id = self._lot_on_hold()

        r1 = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "me.lead", "password": "pass"
        })
        assert r1.status_code == 200
        assert r1.json()["status"] == "waiting_qe_approval"

        r2 = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "qe.engineer", "password": "pass"
        })
        assert r2.status_code == 200
        assert r2.json()["status"] == "ready_for_audit"

    def test_ncr_preserved_after_return(self, seed_catalog):
        batch_id = self._lot_on_hold()
        client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "qe.engineer", "password": "pass"
        })
        r = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "me.lead", "password": "pass"
        })
        assert r.json()["ncr_number"] == "NCR-0001"

    def test_auditor_cannot_sign_return(self, seed_catalog):
        batch_id = self._lot_on_hold()
        response = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "auditor1", "password": "pass"
        })
        assert response.status_code == 403

    def test_double_sign_same_role_fails(self, seed_catalog):
        batch_id = self._lot_on_hold()
        client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "qe.engineer", "password": "pass"
        })
        response = client.patch(f"/lots/{batch_id}/return-from-hold", json={
            "username": "qe.engineer", "password": "pass"
        })
        assert response.status_code == 409