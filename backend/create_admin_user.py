from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.admin_user import AdminUser
from app.security import hash_password

Base.metadata.create_all(bind=engine)

users = [
    ("ptadmin", "CHANGE_THIS_PT_PASSWORD", "pt_admin"),
    ("customeradmin", "CHANGE_THIS_CUSTOMER_PASSWORD", "customer_admin"),
]

db = SessionLocal()

for username, password, role in users:
    existing = db.query(AdminUser).filter(AdminUser.username == username).first()
    if existing:
        print(f"User already exists: {username}")
        continue

    user = AdminUser(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    print(f"Created user: {username}")

db.commit()
db.close()