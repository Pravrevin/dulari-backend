"""
load_data.py
------------
Loads product data from productdata.csv into the PostgreSQL database and
copies product images from the Medicine images folder into media/products/.

Flag assignments
----------------
is_new_launch         : 201, 203, 208, 210, 212, 213, 215, 217, 220, 222
is_trending_near_you  : 1, 3, 4, 8, 33912, 33914, 33919, 33923, 33924, 33925
is_in_spotlight       : 2, 6, 7, 33910, 33911, 33915, 33916, 33917, 33921, 33922

Usage (from the backend/ directory):
    python scripts/load_data.py

The script reads DB credentials from the .env file in the same directory.
"""

import csv
import os
import shutil
import sys
from pathlib import Path

BACKEND_DIR   = Path(__file__).resolve().parent.parent
ENV_FILE      = BACKEND_DIR / ".env"
CSV_FILE      = BACKEND_DIR / "medicine-data-picture" / "productdata.csv"
IMAGES_SRC    = BACKEND_DIR / "medicine-data-picture" / "Medicine images"
IMAGES_DEST   = BACKEND_DIR / "media" / "products"

# ---------- Flag assignments ----------
NEW_LAUNCH_IDS = {201, 203, 208, 210, 212, 213, 215, 217, 220, 222}
TRENDING_IDS   = {1, 3, 4, 8, 33912, 33914, 33919, 33923, 33924, 33925}
SPOTLIGHT_IDS  = {2, 6, 7, 33910, 33911, 33915, 33916, 33917, 33921, 33922}
# --------------------------------------

INSERT_SQL = """
INSERT INTO products_product (
    product_id, product_name, mrp, is_discontinued, manufacturer_name,
    pack_size_label, short_composition1, short_composition2,
    is_new_launch, is_trending_near_you, is_in_spotlight
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (product_id) DO UPDATE SET
    product_name        = EXCLUDED.product_name,
    mrp                 = EXCLUDED.mrp,
    is_discontinued     = EXCLUDED.is_discontinued,
    manufacturer_name   = EXCLUDED.manufacturer_name,
    pack_size_label     = EXCLUDED.pack_size_label,
    short_composition1  = EXCLUDED.short_composition1,
    short_composition2  = EXCLUDED.short_composition2,
    is_new_launch           = EXCLUDED.is_new_launch,
    is_trending_near_you    = EXCLUDED.is_trending_near_you,
    is_in_spotlight         = EXCLUDED.is_in_spotlight;
"""

INSERT_IMAGE_SQL = """
INSERT INTO products_productimage (product_id, image, alt_text)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING;
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


def parse_bool(value: str) -> bool:
    return value.strip().upper() == "TRUE"


def copy_images(product_id: int, cursor) -> int:
    """Copy images for a product into media/products/ and register in DB."""
    src_folder = IMAGES_SRC / str(product_id)
    if not src_folder.exists():
        return 0

    IMAGES_DEST.mkdir(parents=True, exist_ok=True)
    count = 0
    for img_file in sorted(src_folder.iterdir()):
        if not img_file.is_file():
            continue
        dest_name = f"{product_id}_{img_file.name}"
        dest_path = IMAGES_DEST / dest_name
        shutil.copy2(img_file, dest_path)
        # Store relative path used by Django's ImageField
        relative_path = f"products/{dest_name}"
        alt_text = img_file.stem
        cursor.execute(INSERT_IMAGE_SQL, (product_id, relative_path, alt_text))
        count += 1
    return count


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
        "dbname":   env.get("POSTGRES_DB",       "dulari_db"),
        "user":     env.get("POSTGRES_USER",      "dulari_user"),
        "password": env.get("POSTGRES_PASSWORD",  "dulari_pass123"),
        "host":     env.get("POSTGRES_HOST",      "localhost"),
        "port":     env.get("POSTGRES_PORT",      "5432"),
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

    products_loaded = 0
    images_loaded = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = int(row["product_id"])
            params = (
                pid,
                row["product_name"].strip(),
                float(row["mrp"]),
                parse_bool(row["Is_discontinued"]),
                row["manufacturer_name"].strip(),
                row["pack_size_label"].strip(),
                row.get("short_composition1", "").strip(),
                row.get("short_composition2", "").strip(),
                pid in NEW_LAUNCH_IDS,
                pid in TRENDING_IDS,
                pid in SPOTLIGHT_IDS,
            )
            cursor.execute(INSERT_SQL, params)
            products_loaded += 1

            # Copy & register images
            images_loaded += copy_images(pid, cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Done. Loaded {products_loaded} products and {images_loaded} images.")
    print("\nFlag summary:")
    print(f"  New Launches       : {len(NEW_LAUNCH_IDS)} products — IDs: {sorted(NEW_LAUNCH_IDS)}")
    print(f"  Trending Near You  : {len(TRENDING_IDS)} products — IDs: {sorted(TRENDING_IDS)}")
    print(f"  In the Spotlight   : {len(SPOTLIGHT_IDS)} products — IDs: {sorted(SPOTLIGHT_IDS)}")


if __name__ == "__main__":
    main()
