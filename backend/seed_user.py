"""
seed_user.py -- Add a user directly to the PostgreSQL finova database.

Usage:
    python seed_user.py [email] [password]
    python seed_user.py                      # defaults: admin@example.com / admin1234
"""
import sys
import os
from uuid import uuid4

import psycopg2
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

EMAIL    = sys.argv[1] if len(sys.argv) > 1 else "admin@example.com"
PASSWORD = sys.argv[2] if len(sys.argv) > 2 else "admin1234"

# Parse DATABASE_URL_SYNC  → postgresql+psycopg2://user:pass@host:port/db
raw_url = os.getenv("DATABASE_URL_SYNC", "")
# Strip driver prefix so psycopg2 can use it
dsn = raw_url.replace("postgresql+psycopg2://", "postgresql://")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed  = pwd_context.hash(PASSWORD)
user_id = str(uuid4())

try:
    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT email FROM users WHERE email = %s", (EMAIL,))
    if cur.fetchone():
        print(f"WARNING: User '{EMAIL}' already exists -- skipping.")
    else:
        cur.execute(
            "INSERT INTO users (id, email, hashed_password, is_active, created_at) "
            "VALUES (%s, %s, %s, TRUE, now())",
            (user_id, EMAIL, hashed),
        )
        conn.commit()
        print(f"OK: Created user: {EMAIL}  (password: {PASSWORD})")

    # List all users
    cur.execute("SELECT email, is_active, created_at FROM users ORDER BY created_at")
    users = cur.fetchall()
    print(f"\nAll users ({len(users)}):")
    for u in users:
        status = "active" if u[1] else "inactive"
        print(f"  {u[0]}  [{status}]  created: {u[2]}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
