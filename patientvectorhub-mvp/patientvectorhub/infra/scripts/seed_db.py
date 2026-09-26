"""
Seed a demo tenant for local testing.

Usage (from repo root, with DATABASE_URL pointing at the running Postgres,
e.g. after `docker-compose up -d postgres` and running Alembic migrations):

    python infra/scripts/seed_db.py
"""
import os
import uuid
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://pvh:pvh_local_pw@localhost:5432/patientvectorhub",
)


def main():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT id FROM tenants WHERE name = :n"), {"n": "demo-tenant"}).first()
        if existing:
            print(f"demo-tenant already exists: {existing[0]}")
            return
        tenant_id = str(uuid.uuid4())
        conn.execute(
            text("INSERT INTO tenants (id, name, created_at) VALUES (:id, :name, now())"),
            {"id": tenant_id, "name": "demo-tenant"},
        )
        print(f"created demo-tenant: {tenant_id}")


if __name__ == "__main__":
    main()
