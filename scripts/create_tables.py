"""
create_tables.py
----------------
Reads sql/create_tables.sql and executes it against the configured PostgreSQL database.

Usage (from the backend/ directory):
    python scripts/create_tables.py

The script reads DB credentials from the .env file in the same directory.
"""

import os
import sys
from pathlib import Path

# Allow running from any working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
SQL_FILE = BACKEND_DIR / "sql" / "create_tables.sql"
ENV_FILE = BACKEND_DIR / ".env"


def load_env(env_path: Path) -> dict:
    """Parse key=value lines from .env file."""
    env = {}
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

    env = load_env(ENV_FILE)

    db_config = {
        "dbname":   env.get("POSTGRES_DB",       "dulari_db"),
        "user":     env.get("POSTGRES_USER",      "dulari_user"),
        "password": env.get("POSTGRES_PASSWORD",  "dulari_pass123"),
        "host":     env.get("POSTGRES_HOST",      "localhost"),
        "port":     env.get("POSTGRES_PORT",      "5432"),
    }

    if not SQL_FILE.exists():
        print(f"ERROR: SQL file not found at {SQL_FILE}")
        sys.exit(1)

    sql = SQL_FILE.read_text(encoding="utf-8")

    print(f"Connecting to PostgreSQL at {db_config['host']}:{db_config['port']} ...")
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        conn.close()
        print("Tables created successfully.")
    except psycopg2.OperationalError as e:
        print(f"ERROR: Could not connect to the database.\n{e}")
        print("\nMake sure the Docker container is running:  docker-compose up -d db")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
