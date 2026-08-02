import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app
import db_models

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Lot Traceability System is running"}


def test_create_lot():
    new_lot = {
        "id": "TEST001",
        "part_number": "PN100",
        "description": "Test cannula",
        "product_family": "instruments",
        "units": 50,
        "manufacturing_date": "2026-05-10",
        "status": "ready_for_audit"
    }
    response = client.post("/lots", json= new_lot)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "TEST001"
    assert body["status"] == "ready_for_audit"
    assert body["audited_by"] is None


def test_full_lifecycle():
    new_lot = {
        "id": "LIFE001",
        "part_number": "PN-200",
        "description": "Test drape",
        "product_family": "drapes",
        "units": 100,
        "manufacturing_date": "2026-06-01",
        "status": "ready_for_audit"
    }
    client.post("/lots", json=new_lot)

    auditor = {
        "first_name": "Daisy",
        "last_name": "Roberts",
        "system_user": "DRoberts"
    }
    audit_response = client.patch("/lots/LIFE001/audit", json=auditor)
    assert audit_response.status_code == 200
    assert audit_response.json()["status"] == "in_audit_process"
    assert audit_response.json()["audited_by"]["system_user"] == "DRoberts"


    disp_response = client.patch("/lots/LIFE001/disposition?decision=released")
    assert disp_response.status_code == 200
    assert disp_response.json()["status"] == "released"


def test_audit_nonexistent_lot():
    auditor = {
        "first_name": "Daisy",
        "last_name": "Roberts",
        "system_user": "DRoberts"
    }
    response = client.patch("/lots/DOESNOTEXIST/audit", json=auditor)
    assert response.status_code == 404


def test_audit_lot_twice_fails():
    new_lot = {
        "id": "DUPLICATED001",
        "part_number": "PN-300",
        "description": "Test needle",
        "product_family": "needles",
        "units": 200, 
        "manufacturing_date": "2026-07-01",
        "status": "ready_for_audit" 
    }
    client.post("/lots", json=new_lot)
    auditor = {"first_name": "Amy", "last_name": "Cooper", "system_user": "ACooper"}

    first = client.patch("/lots/DUPLICATED001/audit", json=auditor)
    assert first.status_code == 200

    second = client.patch("/lots/DUPLICATED001/audit", json=auditor)
    assert second.status_code == 409

def test_dispose_without_audit_fails():
    new_lot = {
        "id": "NOAUDIT001",
        "part_number": "PN-400",
        "description": "Test container",
        "product_family": "containers",
        "units": 300,
        "manufacturing_date": "2026-07-18",
        "status": "ready_for_audit"
    }
    client.post("/lots", json=new_lot)
    response = client.patch("/lots/NOAUDIT001/disposition?decision=released")
    assert response.status_code == 409