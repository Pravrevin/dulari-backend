"""
load_combos.py
--------------
Loads Combo data from combodata.csv into the products_combo table.
Each combo links two products from productdata.csv with a combo name,
tags, and a combo price.

Usage (from the dulari-backend/ directory):
    python scripts/load_combos.py

Reads DB credentials from the .env file in the same directory.
"""

import csv
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE    = BACKEND_DIR / ".env"
COMBO_CSV   = BACKEND_DIR / "medicine-data-picture" / "combodata.csv"

UPSERT_SQL = """
INSERT INTO products_combo (id, combo_name, product1_id, product2_id, tags, combo_price, is_active)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id)
DO UPDATE SET
    combo_name  = EXCLUDED.combo_name,
    product1_id = EXCLUDED.product1_id,
    product2_id = EXCLUDED.product2_id,
    tags        = EXCLUDED.tags,
    combo_price = EXCLUDED.combo_price,
    is_active   = EXCLUDED.is_active;
"""


def load_env(env_path: Path) -> dict:
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

    if not COMBO_CSV.exists():
        print(f"ERROR: CSV not found at {COMBO_CSV}")
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

    loaded = 0
    with open(COMBO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combo_id    = int(row["combo_id"])
            combo_name  = row["combo_name"].strip()
            product1_id = int(row["product1_id"])
            product2_id = int(row["product2_id"])
            tags        = json.dumps([t.strip() for t in row["tags"].split(",")])
            combo_price = float(row["combo_price"])
            is_active   = row["is_active"].strip().upper() == "TRUE"

            cursor.execute(UPSERT_SQL, (
                combo_id, combo_name, product1_id, product2_id,
                tags, combo_price, is_active,
            ))
            loaded += 1
            print(
                f"  Upserted  [{combo_id}] {combo_name:<35} "
                f"products ({product1_id}, {product2_id})  "
                f"price Rs.{combo_price:.2f}"
            )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nDone. {loaded} combos upserted.")


if __name__ == "__main__":
    main()
