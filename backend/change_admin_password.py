from app.db.session import SessionLocal
from app.models.admin_user import AdminUser
from app.security import hash_password

USERNAME = "ptadmin"
NEW_PASSWORD = "ZxcvPWD"

db = SessionLocal()

user = db.query(AdminUser).filter(
    AdminUser.username == USERNAME
).first()

if not user:
    print("User not found")
    exit()

user.password_hash = hash_password(NEW_PASSWORD)

db.commit()

print(f"Password updated for {USERNAME}")

db.close()
