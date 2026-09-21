"""
Seed completo para Lot Tracker.

ADVERTENCIA:
Este script ELIMINA los datos actuales de:
    - lots
    - part_numbers
    - product_families
    - users

Después crea una base de datos de demostración con:
    - Usuarios ficticios
    - Familias de productos
    - Part numbers reales de Intuitive
    - Lotes de prueba en diferentes estados

Ejecutar desde la raíz del proyecto:

    python seed_database.py
"""

from datetime import date, datetime, timedelta
import random

from app.database import SessionLocal, engine, Base
from app.models.db_models import (
    UserDB,
    ProductFamily,
    PartNumber,
    LotDB,
)
from app.auth.security import hash_password


# ============================================================
# CONFIGURACIÓN
# ============================================================

DEFAULT_PASSWORD = "Password123!"

random.seed(42)


# ============================================================
# USUARIOS DE PRUEBA
# ============================================================
#
# Todos son usuarios ficticios.
# Los nombres están hechos para parecer trabajadores
# norteamericanos, pero no representan empleados reales.
#

USERS = [
    {
        "username": "john.miller",
        "first_name": "John",
        "last_name": "Miller",
        "role": "admin",
    },
    {
        "username": "michael.carter",
        "first_name": "Michael",
        "last_name": "Carter",
        "role": "engineer",
    },
    {
        "username": "david.thompson",
        "first_name": "David",
        "last_name": "Thompson",
        "role": "engineer",
    },
    {
        "username": "james.wilson",
        "first_name": "James",
        "last_name": "Wilson",
        "role": "manufacturing",
    },
    {
        "username": "robert.anderson",
        "first_name": "Robert",
        "last_name": "Anderson",
        "role": "manufacturing",
    },
    {
        "username": "william.johnson",
        "first_name": "William",
        "last_name": "Johnson",
        "role": "auditor",
    },
    {
        "username": "daniel.brown",
        "first_name": "Daniel",
        "last_name": "Brown",
        "role": "auditor",
    },
    {
        "username": "jennifer.davis",
        "first_name": "Jennifer",
        "last_name": "Davis",
        "role": "auditor",
    },
]


# ============================================================
# FAMILIAS
# ============================================================

FAMILIES = [
    "EndoWrist Instruments",
    "Energy Instruments",
    "SureForm Stapling",
    "Force Feedback Instruments",
    "Vision Equipment",
    "Access & Accessories",
]


# ============================================================
# PART NUMBERS REALES DE INTUITIVE
# ============================================================
#
# Los códigos y descripciones están basados en el catálogo
# oficial de instrumentos y accesorios da Vinci X/Xi.
#
# family debe coincidir exactamente con FAMILIES.
#

PART_NUMBERS = [
    # --------------------------------------------------------
    # EndoWrist Instruments
    # --------------------------------------------------------
    {
        "code": "470179",
        "description": "Monopolar curved scissors (Hot shears)",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471172",
        "description": "Maryland bipolar forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470184",
        "description": "Permanent cautery spatula",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471344",
        "description": "Curved bipolar dissector",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471400",
        "description": "Long bipolar grasper",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471405",
        "description": "Force bipolar",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471171",
        "description": "Micro bipolar forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470183",
        "description": "Permanent cautery hook",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471205",
        "description": "Fenestrated bipolar forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470327",
        "description": "Medium-large clip applier",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471006",
        "description": "Large needle driver",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470401",
        "description": "Small clip applier",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470194",
        "description": "Mega needle driver",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471296",
        "description": "Large SutureCut needle driver",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471309",
        "description": "Mega SutureCut needle driver",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470230",
        "description": "Large clip applier",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471093",
        "description": "ProGrasp forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470001",
        "description": "Potts scissors",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471048",
        "description": "Long tip forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470318",
        "description": "Small Graptor (grasping retractor)",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471190",
        "description": "Cobra grasper",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470347",
        "description": "Tip-Up fenestrated grasper",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "471049",
        "description": "Cadiere forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470207",
        "description": "Tenaculum forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470007",
        "description": "Round tip scissors",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470181",
        "description": "Resano forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470249",
        "description": "Dual blade retractor",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470215",
        "description": "Cardiac probe grasper",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470246",
        "description": "Atrial retractor short right",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470033",
        "description": "Black diamond micro forceps",
        "family": "EndoWrist Instruments",
    },
    {
        "code": "470036",
        "description": "DeBakey forceps",
        "family": "EndoWrist Instruments",
    },

    # --------------------------------------------------------
    # Energy Instruments
    # --------------------------------------------------------
    {
        "code": "480275",
        "description": "Harmonic ACE curved shears",
        "family": "Energy Instruments",
    },
    {
        "code": "480299",
        "description": "EndoWrist suction irrigator",
        "family": "Energy Instruments",
    },
    {
        "code": "480422",
        "description": "Vessel Sealer Extend",
        "family": "Energy Instruments",
    },
    {
        "code": "480440",
        "description": "SynchroSeal",
        "family": "Energy Instruments",
    },
    {
        "code": "480522",
        "description": "Vessel Sealer Curved",
        "family": "Energy Instruments",
    },

    # --------------------------------------------------------
    # SureForm Stapling
    # --------------------------------------------------------
    {
        "code": "480460",
        "description": "SureForm 60 instrument",
        "family": "SureForm Stapling",
    },
    {
        "code": "480445",
        "description": "SureForm 45 instrument",
        "family": "SureForm Stapling",
    },
    {
        "code": "480545",
        "description": "SureForm 45 curved-tip instrument",
        "family": "SureForm Stapling",
    },
    {
        "code": "488530",
        "description": "8 mm SureForm 30 curved-tip stapler",
        "family": "SureForm Stapling",
    },
    {
        "code": "48360W",
        "description": "Reload, SureForm 60, 2.5 white",
        "family": "SureForm Stapling",
    },
    {
        "code": "48360B",
        "description": "Reload, SureForm 60, 3.5 blue",
        "family": "SureForm Stapling",
    },
    {
        "code": "48360G",
        "description": "Reload, SureForm 60, 4.3 green",
        "family": "SureForm Stapling",
    },
    {
        "code": "48360T",
        "description": "Reload, SureForm 60, 4.6 black",
        "family": "SureForm Stapling",
    },
    {
        "code": "48345M",
        "description": "Reload, SureForm 45, 2.0 gray",
        "family": "SureForm Stapling",
    },
    {
        "code": "48345W",
        "description": "Reload, SureForm 45, 2.5 white",
        "family": "SureForm Stapling",
    },
    {
        "code": "48345B",
        "description": "Reload, SureForm 45, 3.5 blue",
        "family": "SureForm Stapling",
    },
    {
        "code": "48345G",
        "description": "Reload, SureForm 45, 4.3 green",
        "family": "SureForm Stapling",
    },
    {
        "code": "48345T",
        "description": "Reload, SureForm 45, 4.6 black",
        "family": "SureForm Stapling",
    },
    {
        "code": "48230M",
        "description": "Reload, 8 mm SureForm 30, 2.0 gray",
        "family": "SureForm Stapling",
    },
    {
        "code": "48230W",
        "description": "Reload, 8 mm SureForm 30, 2.5 white",
        "family": "SureForm Stapling",
    },
    {
        "code": "48230B",
        "description": "Reload, 8 mm SureForm 30, 3.5 blue",
        "family": "SureForm Stapling",
    },

    # --------------------------------------------------------
    # Force Feedback Instruments
    # --------------------------------------------------------
    {
        "code": "476309",
        "description": "Force Feedback Mega SutureCut needle driver",
        "family": "Force Feedback Instruments",
    },
    {
        "code": "476205",
        "description": "Force Feedback fenestrated bipolar forceps",
        "family": "Force Feedback Instruments",
    },
    {
        "code": "476093",
        "description": "Force Feedback ProGrasp forceps",
        "family": "Force Feedback Instruments",
    },
    {
        "code": "476172",
        "description": "Force Feedback Maryland bipolar forceps",
        "family": "Force Feedback Instruments",
    },
    {
        "code": "476049",
        "description": "Force Feedback Cadiere forceps",
        "family": "Force Feedback Instruments",
    },

    # --------------------------------------------------------
    # Vision Equipment
    # --------------------------------------------------------
    {
        "code": "470056",
        "description": "8 mm endoscope plus, 0 degrees",
        "family": "Vision Equipment",
    },
    {
        "code": "470057",
        "description": "8 mm endoscope plus, 30 degrees",
        "family": "Vision Equipment",
    },
    {
        "code": "470066",
        "description": "Da Vinci 5 Endoscope, 0 degrees",
        "family": "Vision Equipment",
    },
    {
        "code": "470067",
        "description": "Da Vinci 5 Endoscope, 30 degrees",
        "family": "Vision Equipment",
    },
    {
        "code": "470655",
        "description": "NIR Handheld Camera",
        "family": "Vision Equipment",
    },
    {
        "code": "470656",
        "description": "NIR Handheld Camera light guide",
        "family": "Vision Equipment",
    },
    {
        "code": "470657",
        "description": "NIR Handheld Camera light guide adapter",
        "family": "Vision Equipment",
    },
    {
        "code": "470035",
        "description": "da Vinci Handheld Camera (for X/Xi/SP)",
        "family": "Vision Equipment",
    },

    # --------------------------------------------------------
    # Access & Accessories
    # --------------------------------------------------------
    {
        "code": "470375",
        "description": "12 mm and stapler cannula (100 mm)",
        "family": "Access & Accessories",
    },
    {
        "code": "470376",
        "description": "12 mm and stapler blunt obturator",
        "family": "Access & Accessories",
    },
    {
        "code": "470389",
        "description": "12 mm and stapler cannula, long (150 mm)",
        "family": "Access & Accessories",
    },
    {
        "code": "470390",
        "description": "12 mm and stapler blunt obturator, long",
        "family": "Access & Accessories",
    },
    {
        "code": "470500",
        "description": "5 - 12 mm Universal Seal",
        "family": "Access & Accessories",
    },
    {
        "code": "470381",
        "description": "12 - 8 mm reducer",
        "family": "Access & Accessories",
    },
    {
        "code": "470395",
        "description": "12 mm and stapler bladeless obturator",
        "family": "Access & Accessories",
    },
    {
        "code": "470396",
        "description": "12 mm and stapler bladeless obturator, long",
        "family": "Access & Accessories",
    },
    {
        "code": "470008",
        "description": "8 mm blunt obturator",
        "family": "Access & Accessories",
    },
    {
        "code": "470009",
        "description": "8 mm blunt obturator, long",
        "family": "Access & Accessories",
    },
    {
        "code": "470062",
        "description": "8 mm Hex Cannula, standard",
        "family": "Access & Accessories",
    },
    {
        "code": "470064",
        "description": "8 mm Hex Cannula, long",
        "family": "Access & Accessories",
    },
    {
        "code": "470319",
        "description": "8 mm flared/grounded cannula",
        "family": "Access & Accessories",
    },
    {
        "code": "470398",
        "description": "8 mm Hasson cone",
        "family": "Access & Accessories",
    },
    {
        "code": "470399",
        "description": "12 mm Hasson cone",
        "family": "Access & Accessories",
    },
]


# ============================================================
# FUNCIONES
# ============================================================

def clear_database(db):
    """
    Borra los datos respetando el orden de las relaciones
    entre las tablas.
    """

    print("\n[1/5] Eliminando datos actuales...")

    # Primero los lotes porque dependen de part_numbers y users.
    deleted_lots = db.query(LotDB).delete(synchronize_session=False)

    # Después part numbers.
    deleted_parts = db.query(PartNumber).delete(
        synchronize_session=False
    )

    # Después familias.
    deleted_families = db.query(ProductFamily).delete(
        synchronize_session=False
    )

    # Finalmente usuarios.
    deleted_users = db.query(UserDB).delete(
        synchronize_session=False
    )

    db.commit()

    print(f"      Lots eliminados: {deleted_lots}")
    print(f"      Part numbers eliminados: {deleted_parts}")
    print(f"      Familias eliminadas: {deleted_families}")
    print(f"      Usuarios eliminados: {deleted_users}")


def create_users(db):
    print("\n[2/5] Creando usuarios...")

    created = {}

    for data in USERS:
        user = UserDB(
            username=data["username"],
            hashed_password=hash_password(DEFAULT_PASSWORD),
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=data["role"],
            is_active="true",
        )

        db.add(user)
        created[data["username"]] = user

    db.commit()

    for user in created.values():
        db.refresh(user)

    print(f"      Usuarios creados: {len(created)}")

    return created


def create_families(db, users):
    print("\n[3/5] Creando familias...")

    engineer = users["michael.carter"].username

    families = {}

    for name in FAMILIES:
        family = ProductFamily(
            name=name,
            status="active",
            proposed_by=engineer,
            approved_by=engineer,
        )

        db.add(family)
        families[name] = family

    db.commit()

    for family in families.values():
        db.refresh(family)

    print(f"      Familias creadas: {len(families)}")

    return families


def create_part_numbers(db, users):
    print("\n[4/5] Creando part numbers...")

    engineer_proposer = users["michael.carter"].username
    engineer_approver = users["david.thompson"].username

    created = {}

    for data in PART_NUMBERS:
        part = PartNumber(
            code=data["code"],
            description=data["description"],
            family_name=data["family"],
            status="active",
            proposed_by=engineer_proposer,
            approved_by=engineer_approver,
        )

        db.add(part)
        created[data["code"]] = part

    db.commit()

    for part in created.values():
        db.refresh(part)

    print(f"      Part numbers creados: {len(created)}")

    return created


def random_manufacturing_date(days_back_min=30, days_back_max=365):
    """
    Genera una fecha de fabricación dentro de un rango
    razonable para datos de demostración.
    """

    days_back = random.randint(
        days_back_min,
        days_back_max,
    )

    return date.today() - timedelta(days=days_back)


def create_lots(db, users, part_numbers):
    print("\n[5/5] Creando lotes...")

    auditors = [
        users["william.johnson"],
        users["daniel.brown"],
        users["jennifer.davis"],
    ]

    manufacturing_users = [
        users["james.wilson"],
        users["robert.anderson"],
    ]

    engineers = [
        users["michael.carter"],
        users["david.thompson"],
    ]

    part_codes = list(part_numbers.keys())

    created_count = 0

    # --------------------------------------------------------
    # Lotes READY_FOR_AUDIT
    # --------------------------------------------------------

    for i in range(1, 16):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=random_manufacturing_date(),
            status="ready_for_audit",
        )

        db.add(lot)
        created_count += 1

    # --------------------------------------------------------
    # Lotes IN_AUDIT_PROCESS
    # --------------------------------------------------------

    for i in range(16, 21):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]
        auditor = auditors[(i - 16) % len(auditors)]

        manufacturing_date = random_manufacturing_date()

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=manufacturing_date,
            status="in_audit_process",
            audited_by_first_name=auditor.first_name,
            audited_by_last_name=auditor.last_name,
            audited_by_system_user=auditor.username,
            audited_at=datetime.now() - timedelta(
                hours=random.randint(1, 48)
            ),
        )

        db.add(lot)
        created_count += 1

    # --------------------------------------------------------
    # Lotes RELEASED
    # --------------------------------------------------------

    for i in range(21, 31):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]
        auditor = auditors[(i - 21) % len(auditors)]

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=random_manufacturing_date(),
            status="released",
            audited_by_first_name=auditor.first_name,
            audited_by_last_name=auditor.last_name,
            audited_by_system_user=auditor.username,
            audited_at=datetime.now() - timedelta(
                days=random.randint(1, 15)
            ),
        )

        db.add(lot)
        created_count += 1

    # --------------------------------------------------------
    # Lotes HOLD
    # --------------------------------------------------------

    for i in range(31, 36):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]
        auditor = auditors[(i - 31) % len(auditors)]

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=random_manufacturing_date(),
            status="hold",
            audited_by_first_name=auditor.first_name,
            audited_by_last_name=auditor.last_name,
            audited_by_system_user=auditor.username,
            audited_at=datetime.now() - timedelta(
                days=random.randint(1, 10)
            ),
            ncr_number=f"NCR-2026-{i:04d}",
        )

        db.add(lot)
        created_count += 1

    # --------------------------------------------------------
    # WAITING_ME_APPROVAL
    # --------------------------------------------------------
    #
    # QE ya firmó, Manufacturing todavía no.
    #

    for i in range(36, 39):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]
        auditor = auditors[(i - 36) % len(auditors)]

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=random_manufacturing_date(),
            status="waiting_me_approval",
            audited_by_first_name=auditor.first_name,
            audited_by_last_name=auditor.last_name,
            audited_by_system_user=auditor.username,
            audited_at=datetime.now() - timedelta(days=2),
            qe_approved_by=engineers[
                (i - 36) % len(engineers)
            ].username,
        )

        db.add(lot)
        created_count += 1

    # --------------------------------------------------------
    # WAITING_QE_APPROVAL
    # --------------------------------------------------------
    #
    # Manufacturing ya firmó, QE todavía no.
    #

    for i in range(39, 42):
        code = part_codes[(i - 1) % len(part_codes)]
        part = part_numbers[code]
        auditor = auditors[(i - 39) % len(auditors)]

        lot = LotDB(
            lot_id=f"LOT-2026-{i:04d}",
            part_number_code=code,
            product_family=part.family_name,
            units=random.randint(20, 250),
            manufacturing_date=random_manufacturing_date(),
            status="waiting_qe_approval",
            audited_by_first_name=auditor.first_name,
            audited_by_last_name=auditor.last_name,
            audited_by_system_user=auditor.username,
            audited_at=datetime.now() - timedelta(days=3),
            me_approved_by=manufacturing_users[
                (i - 39) % len(manufacturing_users)
            ].username,
        )

        db.add(lot)
        created_count += 1

    db.commit()

    print(f"      Lotes creados: {created_count}")

    return created_count


def print_summary(db):
    print("\n" + "=" * 60)
    print("BASE DE DATOS POBLADA CORRECTAMENTE")
    print("=" * 60)

    print(f"Usuarios:       {db.query(UserDB).count()}")
    print(f"Familias:       {db.query(ProductFamily).count()}")
    print(f"Part numbers:   {db.query(PartNumber).count()}")
    print(f"Lotes:          {db.query(LotDB).count()}")

    print("\nEstados de lotes:")

    statuses = [
        "ready_for_audit",
        "in_audit_process",
        "released",
        "hold",
        "waiting_me_approval",
        "waiting_qe_approval",
    ]

    for status in statuses:
        count = (
            db.query(LotDB)
            .filter(LotDB.status == status)
            .count()
        )

        print(f"  {status:<25} {count}")

    print("\nUsuarios de prueba:")
    print("-" * 60)

    for user in USERS:
        print(
            f"  {user['username']:<22} "
            f"{user['role']:<14} "
            f"password: {DEFAULT_PASSWORD}"
        )

    print("\n" + "=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("LOT TRACKER - DATABASE SEED")
    print("=" * 60)

    print("\nATENCIÓN:")
    print("Este proceso eliminará TODOS los datos actuales.")
    print("La base será repoblada con datos de demostración.")

    db = SessionLocal()

    try:
        # Asegura que las tablas existan.
        Base.metadata.create_all(bind=engine)

        # 1. Limpiar.
        clear_database(db)

        # 2. Usuarios.
        users = create_users(db)

        # 3. Familias.
        create_families(db, users)

        # 4. Part numbers.
        part_numbers = create_part_numbers(db, users)

        # 5. Lotes.
        create_lots(db, users, part_numbers)

        # Resumen.
        print_summary(db)

    except Exception as exc:
        db.rollback()

        print("\n" + "=" * 60)
        print("ERROR DURANTE EL SEED")
        print("=" * 60)
        print(str(exc))

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()

