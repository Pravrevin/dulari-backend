"""
load_generic_medicine.py
------------------------
Loads generic medicines from generic_medicine.csv into the PostgreSQL database.
For each generic medicine, it reuses the first existing product image (from
media/products/) as the generic medicine image — copies it to media/generic_medicines/.
If no product image exists, the image field is left blank.

Usage (from the dulari-backend/ directory):
    python scripts/load_generic_medicine.py

Reads DB credentials from the .env file in the same directory.
"""

import csv
import shutil
import sys
from pathlib import Path

BACKEND_DIR      = Path(__file__).resolve().parent.parent
ENV_FILE         = BACKEND_DIR / ".env"
CSV_FILE         = BACKEND_DIR / "medicine-data-picture" / "generic_medicine.csv"
# Downloaded images live here (one sub-folder per generic_product_id)
IMAGES_SRC       = BACKEND_DIR / "medicine-data-picture" / "generic_medicine_images"
IMAGES_DEST      = BACKEND_DIR / "media" / "generic_medicines"

INSERT_SQL = """
INSERT INTO products_genericmedicine (
    generic_product_id, name, brand, mrp, discount_percentage, image, product_id
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (generic_product_id) DO UPDATE SET
    name                = EXCLUDED.name,
    brand               = EXCLUDED.brand,
    mrp                 = EXCLUDED.mrp,
    discount_percentage = EXCLUDED.discount_percentage,
    image               = EXCLUDED.image,
    product_id          = EXCLUDED.product_id;
"""

FETCH_PRODUCT_MRPS_SQL = "SELECT product_id, mrp FROM products_product;"


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


def find_downloaded_image(generic_product_id: int) -> Path | None:
    """Return the downloaded image for this generic medicine, or None."""
    folder = IMAGES_SRC / str(generic_product_id)
    if not folder.exists():
        return None
    matches = sorted(folder.iterdir())
    return matches[0] if matches else None


def copy_image_for_generic(generic_product_id: int) -> str:
    """
    Copy the downloaded generic medicine image into media/generic_medicines/.
    Returns the relative media path or empty string if no image found.
    """
    src = find_downloaded_image(generic_product_id)
    if src is None:
        return ""

    IMAGES_DEST.mkdir(parents=True, exist_ok=True)
    dest_name = f"gen_{generic_product_id}{src.suffix}"
    dest_path = IMAGES_DEST / dest_name
    shutil.copy2(src, dest_path)
    return f"generic_medicines/{dest_name}"


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

    # Pre-fetch all product MRPs so we can calculate discount_percentage per row
    cursor.execute(FETCH_PRODUCT_MRPS_SQL)
    product_mrp_map = {row[0]: float(row[1]) for row in cursor.fetchall()}
    print(f"  Loaded MRPs for {len(product_mrp_map)} products.")

    loaded = 0
    images_copied = 0
    no_image = []

    print("Loading generic medicines ...")
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid        = int(row["generic_product_id"])
            product_id = int(row["product_id"])
            name       = row["name"].strip()
            brand      = row["brand"].strip()
            generic_mrp = float(row["mrp"])

            # Calculate discount % vs the branded product MRP
            product_mrp = product_mrp_map.get(product_id, 0)
            if product_mrp > 0:
                discount_pct = round(((product_mrp - generic_mrp) / product_mrp) * 100, 2)
                # Cap at 0 in the unlikely case generic is more expensive
                discount_pct = max(discount_pct, 0)
            else:
                discount_pct = 0.0

            image_path = copy_image_for_generic(gid)
            if image_path:
                images_copied += 1
            else:
                no_image.append(gid)

            cursor.execute(INSERT_SQL, (gid, name, brand, generic_mrp, discount_pct, image_path, product_id))
            loaded += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nDone.")
    print(f"  Generic medicines loaded : {loaded}")
    print(f"  Images copied            : {images_copied}")
    if no_image:
        print(f"  No image found for IDs   : {no_image}")
    else:
        print(f"  All generic medicines have an image.")
    print(f"\n  Discount % calculated as: ((branded_mrp - generic_mrp) / branded_mrp) * 100")


if __name__ == "__main__":
    main()
