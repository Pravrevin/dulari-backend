"""
load_super_saving_deals.py
--------------------------
Loads Super Saving Deals by picking 6 products from productdata.csv
and inserting them into the products_supersavingdeal table.

Usage (from the dulari-backend/ directory):
    python scripts/load_super_saving_deals.py

Reads DB credentials from the .env file in the same directory.
"""

import csv
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE    = BACKEND_DIR / ".env"
CSV_FILE    = BACKEND_DIR / "medicine-data-picture" / "productdata.csv"

# product_id -> discount_percentage to apply (all > 50%)
DEALS = {
    1:     55.00,   # Augmentin 625 Duo Tablet       MRP 223.42
    4:     52.00,   # Allegra 120mg Tablet            MRP 218.81
    33910: 60.00,   # Chymoral Forte Tablet           MRP 423.40
    33912: 58.00,   # Combiflam Tablet                MRP  46.05
    33925: 65.00,   # Crocin Pain Relief Tablet       MRP  65.73
    33916: 70.00,   # Ceftum 500mg Tablet             MRP 474.05
}

# Upsert: update existing row for this product, insert if not present
UPSERT_SQL = """
INSERT INTO products_supersavingdeal (product_id, discount_percentage, discounted_price, is_active)
VALUES (%s, %s, %s, %s)
ON CONFLICT (product_id)
DO UPDATE SET
    discount_percentage = EXCLUDED.discount_percentage,
    discounted_price    = EXCLUDED.discounted_price,
    is_active           = EXCLUDED.is_active;
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

    # Build a lookup from the CSV for the products we need
    products = {}
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = int(row["product_id"])
            if pid in DEALS:
                products[pid] = {
                    "name": row["product_name"],
                    "mrp":  float(row["mrp"]),
                }

    print(f"Found {len(products)}/{len(DEALS)} products in CSV. Loading deals ...")

    loaded = 0
    for product_id, discount_pct in DEALS.items():
        if product_id not in products:
            print(f"  SKIP  product_id={product_id} — not found in CSV")
            continue

        info = products[product_id]
        mrp = info["mrp"]
        discounted_price = round(mrp - (mrp * discount_pct / 100), 2)

        cursor.execute(UPSERT_SQL, (product_id, discount_pct, discounted_price, True))
        loaded += 1
        print(
            f"  Upserted  {info['name']:<45} "
            f"MRP Rs.{mrp:>7.2f}  -> {discount_pct:.0f}% off  -> Rs.{discounted_price:.2f}"
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nDone. {loaded} super saving deals upserted.")


if __name__ == "__main__":
    main()
