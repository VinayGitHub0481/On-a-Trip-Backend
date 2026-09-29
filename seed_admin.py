"""
Run this once to create the first admin account, since /auth/register
requires an existing admin to call it (bootstrap problem).

Usage: python seed_admin.py
"""

from app.db.database import SessionLocal, Base, engine
from app.models.user import User, RoleEnum
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

email = input("Admin email: ").strip()
name = input("Admin name: ").strip()
password = input("Admin password: ").strip()

existing = db.query(User).filter(User.email == email).first()
if existing:
    print("A user with that email already exists.")
else:
    admin = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=RoleEnum.admin,
    )
    db.add(admin)
    db.commit()
    print(f"Admin '{email}' created successfully.")

db.close()
