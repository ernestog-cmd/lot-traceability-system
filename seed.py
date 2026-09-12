from app.database import SessionLocal
from app.models.db_models import UserDB
from app.auth.security import hash_password

db = SessionLocal()

admin = UserDB(
    username="admin",
    hashed_password=hash_password("admin123"),
    first_name="Admin",
    last_name="System",
    role="admin"
)

db.add(admin)
db.commit()
db.close()

print("Admin user created: admin / admin123")