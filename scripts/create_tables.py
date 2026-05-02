"""
create_tables.py
----------------
Drops all existing app tables, recreates them from sql/create_tables.sql,
and fakes Django migrations so manage.py stays in sync.

Usage (from the dulari-backend/ directory):
    python scripts/create_tables.py

Reads DB credentials from the .env file in the same directory.
"""

import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
SQL_FILE    = BACKEND_DIR / "sql" / "create_tables.sql"
ENV_FILE    = BACKEND_DIR / ".env"

DJANGO_MIGRATION_APPS = ("products",)

CLEAN_MIGRATIONS_SQL = "DELETE FROM django_migrations WHERE app = ANY(%s);"


def load_env(env_path: Path) -> dict:
    import os
    env = dict(os.environ)
    if not env_path.exists():
        return env
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def main():
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    if not SQL_FILE.exists():
        print(f"ERROR: SQL file not found at {SQL_FILE}")
        sys.exit(1)

    env = load_env(ENV_FILE)
    db_config = {
        "dbname":   env.get("POSTGRES_DB",      "dulari_db"),
        "user":     env.get("POSTGRES_USER",     "dulari_user"),
        "password": env.get("POSTGRES_PASSWORD", "dulari_pass123"),
        "host":     env.get("POSTGRES_HOST",     "localhost"),
        "port":     env.get("POSTGRES_PORT",     "5433"),
    }

    print(f"Connecting to PostgreSQL at {db_config['host']}:{db_config['port']} ...")
    try:
        conn = psycopg2.connect(**db_config)
    except psycopg2.OperationalError as e:
        print(f"ERROR: Could not connect.\n{e}")
        print("Make sure the Docker container is running:  docker-compose up -d db")
        sys.exit(1)

    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # 1. Drop & recreate tables from SQL file
        print("Dropping and recreating tables ...")
        cursor.execute(SQL_FILE.read_text(encoding="utf-8"))

        # 2. Clear Django migration history for app tables (if table exists)
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'django_migrations'
            )
        """)
        if cursor.fetchone()[0]:
            cursor.execute(CLEAN_MIGRATIONS_SQL, (list(DJANGO_MIGRATION_APPS),))
            print(f"Cleared Django migration history for: {', '.join(DJANGO_MIGRATION_APPS)}")

        conn.commit()
        print("Schema recreated successfully.")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    # 3. Fake Django migrations so manage.py migrate stays in sync
    print("Faking Django migrations ...")
    result = subprocess.run(
        [sys.executable, str(BACKEND_DIR / "manage.py"), "migrate", "--fake"],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(f"WARNING: migrate --fake failed:\n{result.stderr.strip()}")

    print("\nDone. Schema is clean and Django migrations are synced.")
    print("Next step:  python scripts/load_data.py")


if __name__ == "__main__":
    main()
