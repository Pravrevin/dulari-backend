"""
load_deals.py
-------------
Loads deals-of-the-day from deals_of_the_day.csv into the PostgreSQL database.

Usage (from the dulari-backend/ directory):
    python scripts/load_deals.py

Reads DB credentials from the .env file in the same directory.
"""

import csv
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE    = BACKEND_DIR / ".env"
CSV_FILE    = BACKEND_DIR / "medicine-data-picture" / "deals_of_the_day.csv"

INSERT_DEAL_SQL = """
INSERT INTO products_dealoftheday (product_id, discount_percentage, discounted_price, offer_ends_at, is_active)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
"""


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


def parse_bool(value: str) -> bool:
    return value.strip().upper() == "TRUE"


def main():
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    if not CSV_FILE.exists():
        print(f"ERROR: CSV not found at {CSV_FILE}")
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
    except Exception as e:
        print(f"ERROR: Could not connect.\n{e}")
        print("Make sure the Docker container is running:  docker-compose up -d db")
        sys.exit(1)

    conn.autocommit = False
    cursor = conn.cursor()

    print("Loading deals of the day ...")
    deals_loaded = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(INSERT_DEAL_SQL, (
                int(row["product_id"]),
                float(row["discount_percentage"]),
                float(row["discounted_price"]),
                row["offer_ends_at"].strip(),
                parse_bool(row["is_active"]),
            ))
            deals_loaded += 1
            print(f"  Inserted deal: {row['product_name']} — {row['discount_percentage']}% off")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nDone. {deals_loaded} deals loaded.")


if __name__ == "__main__":
    main()
