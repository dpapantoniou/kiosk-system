from app.db.session import SessionLocal
from app.models.admin_user import AdminUser

db = SessionLocal()

users = db.query(AdminUser).all()

print(f"Found {len(users)} users")

for u in users:
    print(
        f"id={u.id} "
        f"username={u.username} "
        f"role={u.role} "
        f"active={u.is_active}"
    )

db.close()
