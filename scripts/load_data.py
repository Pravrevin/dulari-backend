"""
load_data.py
------------
Loads categories, product data from productdata.csv, and product images
into the PostgreSQL database.

Usage (from the dulari-backend/ directory):
    python scripts/load_data.py

Reads DB credentials from the .env file in the same directory.
"""

import csv
import shutil
import sys
from pathlib import Path

BACKEND_DIR          = Path(__file__).resolve().parent.parent
ENV_FILE             = BACKEND_DIR / ".env"
CSV_FILE             = BACKEND_DIR / "medicine-data-picture" / "productdata.csv"
FEATURES_CSV_FILE    = BACKEND_DIR / "medicine-data-picture" / "product_features.csv"
IMAGES_SRC           = BACKEND_DIR / "medicine-data-picture" / "Medicine images"
IMAGES_DEST          = BACKEND_DIR / "media" / "products"
CATEGORY_IMAGES_SRC  = BACKEND_DIR / "medicine-data-picture" / "category_images"
CATEGORY_IMAGES_DEST = BACKEND_DIR / "media" / "categories"

# ---------- Flag assignments ----------
NEW_LAUNCH_IDS = {201, 203, 208, 210, 212, 213, 215, 217, 220, 222}
TRENDING_IDS   = {1, 3, 4, 8, 33912, 33914, 33919, 33923, 33924, 33925}
SPOTLIGHT_IDS  = {2, 6, 7, 33910, 33911, 33915, 33916, 33917, 33921, 33922}

# ---------- Categories ----------
# Each entry: (name, description)
CATEGORIES = [
    ("Antibiotics",             "Medicines that treat bacterial infections"),
    ("Allergy & Antihistamines","Medicines for allergic reactions and histamine control"),
    ("Respiratory & Cough",     "Medicines for cough, cold, asthma, and breathing issues"),
    ("Pain Relief",             "Analgesics and anti-inflammatory medicines"),
    ("Cardiovascular",          "Medicines for heart, blood pressure, and cholesterol"),
    ("Gastrointestinal",        "Medicines for stomach, acidity, and digestive issues"),
    ("Diabetes Care",           "Medicines for blood sugar management"),
    ("Neurology & Mental Health","Medicines for nerves, anxiety, and pain management"),
    ("Dermatology",             "Medicines for skin conditions and infections"),
    ("Eye & Ear Care",          "Drops and medicines for eye and ear conditions"),
    ("Vitamins & Supplements",  "Vitamins, minerals, and nutritional supplements"),
    ("Urology",                 "Medicines for urinary tract and bladder conditions"),
]

# ---------- Product → Category mapping ----------
# product_id: category name (must match CATEGORIES above)
PRODUCT_CATEGORY = {
    # Antibiotics
    1: "Antibiotics", 2: "Antibiotics", 7: "Antibiotics", 8: "Antibiotics",
    14: "Antibiotics", 20: "Antibiotics", 27: "Antibiotics", 43: "Antibiotics",
    45: "Antibiotics", 46: "Antibiotics", 47: "Antibiotics", 49: "Antibiotics",
    206: "Antibiotics", 208: "Antibiotics", 216: "Antibiotics",
    33913: "Antibiotics", 33916: "Antibiotics", 33919: "Antibiotics",
    33923: "Antibiotics", 50704: "Antibiotics",

    # Allergy & Antihistamines
    4: "Allergy & Antihistamines", 5: "Allergy & Antihistamines",
    6: "Allergy & Antihistamines", 9: "Allergy & Antihistamines",
    17: "Allergy & Antihistamines", 19: "Allergy & Antihistamines",
    28: "Allergy & Antihistamines", 31: "Allergy & Antihistamines",
    32: "Allergy & Antihistamines", 33911: "Allergy & Antihistamines",
    33915: "Allergy & Antihistamines",

    # Respiratory & Cough
    3: "Respiratory & Cough", 10: "Respiratory & Cough", 12: "Respiratory & Cough",
    15: "Respiratory & Cough", 18: "Respiratory & Cough", 21: "Respiratory & Cough",
    25: "Respiratory & Cough", 26: "Respiratory & Cough", 42: "Respiratory & Cough",
    44: "Respiratory & Cough", 50: "Respiratory & Cough", 202: "Respiratory & Cough",
    205: "Respiratory & Cough", 218: "Respiratory & Cough", 221: "Respiratory & Cough",

    # Pain Relief
    23: "Pain Relief", 37: "Pain Relief", 41: "Pain Relief", 48: "Pain Relief",
    33910: "Pain Relief", 33912: "Pain Relief", 33924: "Pain Relief", 33925: "Pain Relief",

    # Cardiovascular
    16: "Cardiovascular", 30: "Cardiovascular", 33: "Cardiovascular", 34: "Cardiovascular",
    203: "Cardiovascular", 204: "Cardiovascular", 215: "Cardiovascular",
    217: "Cardiovascular", 220: "Cardiovascular", 222: "Cardiovascular",
    33921: "Cardiovascular",

    # Gastrointestinal
    11: "Gastrointestinal", 29: "Gastrointestinal", 219: "Gastrointestinal",
    33914: "Gastrointestinal", 33920: "Gastrointestinal", 33922: "Gastrointestinal",

    # Diabetes Care
    209: "Diabetes Care", 212: "Diabetes Care", 213: "Diabetes Care", 214: "Diabetes Care",

    # Neurology & Mental Health
    22: "Neurology & Mental Health", 24: "Neurology & Mental Health",
    35: "Neurology & Mental Health", 39: "Neurology & Mental Health",
    207: "Neurology & Mental Health", 210: "Neurology & Mental Health",

    # Dermatology
    13: "Dermatology", 201: "Dermatology", 223: "Dermatology", 33917: "Dermatology",

    # Eye & Ear Care
    33918: "Eye & Ear Care",

    # Vitamins & Supplements
    40: "Vitamins & Supplements",

    # Urology
    36: "Urology", 38: "Urology", 211: "Urology",
}

# ---------- SQL ----------
INSERT_CATEGORY_SQL = """
INSERT INTO products_category (name, description, count_of_products)
VALUES (%s, %s, 0)
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description, count_of_products = 0
RETURNING id, name;
"""

INSERT_PRODUCT_SQL = """
INSERT INTO products_product (
    product_id, product_name, mrp, is_discontinued, manufacturer_name,
    pack_size_label, short_composition1, short_composition2, category_id,
    is_new_launch, is_trending_near_you, is_in_spotlight, is_approved
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (product_id) DO UPDATE SET
    product_name        = EXCLUDED.product_name,
    mrp                 = EXCLUDED.mrp,
    is_discontinued     = EXCLUDED.is_discontinued,
    manufacturer_name   = EXCLUDED.manufacturer_name,
    pack_size_label     = EXCLUDED.pack_size_label,
    short_composition1  = EXCLUDED.short_composition1,
    short_composition2  = EXCLUDED.short_composition2,
    category_id         = EXCLUDED.category_id,
    is_new_launch           = EXCLUDED.is_new_launch,
    is_trending_near_you    = EXCLUDED.is_trending_near_you,
    is_in_spotlight         = EXCLUDED.is_in_spotlight,
    is_approved             = EXCLUDED.is_approved;
"""

INSERT_IMAGE_SQL = """
INSERT INTO products_productimage (product_id, image, alt_text)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING;
"""

INSERT_FEATURE_SQL = """
INSERT INTO products_productfeature (
    product_id, description, uses, benefits, side_effects, how_to_use, substitutes
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (product_id) DO UPDATE SET
    description  = EXCLUDED.description,
    uses         = EXCLUDED.uses,
    benefits     = EXCLUDED.benefits,
    side_effects = EXCLUDED.side_effects,
    how_to_use   = EXCLUDED.how_to_use,
    substitutes  = EXCLUDED.substitutes;
"""

UPDATE_CATEGORY_IMAGE_SQL = """
UPDATE products_category SET image = %s WHERE id = %s;
"""

UPDATE_CATEGORY_COUNT_SQL = """
UPDATE products_category c
SET count_of_products = (
    SELECT COUNT(*) FROM products_product p WHERE p.category_id = c.id
);
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


def copy_category_image(category_id: int, folder_index: int, cursor) -> bool:
    """folder_index is the 1-based position of the category in CATEGORIES; folders on disk are named 1..N to match."""
    src_folder = CATEGORY_IMAGES_SRC / str(folder_index)
    if not src_folder.exists():
        return False
    CATEGORY_IMAGES_DEST.mkdir(parents=True, exist_ok=True)
    for img_file in sorted(src_folder.iterdir()):
        if not img_file.is_file():
            continue
        dest_name = f"{category_id}_{img_file.name}"
        dest_path = CATEGORY_IMAGES_DEST / dest_name
        shutil.copy2(img_file, dest_path)
        cursor.execute(UPDATE_CATEGORY_IMAGE_SQL, (f"categories/{dest_name}", category_id))
        return True
    return False


def copy_images(product_id: int, cursor) -> int:
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
        cursor.execute(INSERT_IMAGE_SQL, (product_id, f"products/{dest_name}", img_file.stem))
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

    # 1. Insert categories and build name→id map
    print("Loading categories ...")
    category_map = {}
    category_images_loaded = 0
    for idx, (name, description) in enumerate(CATEGORIES, start=1):
        cursor.execute(INSERT_CATEGORY_SQL, (name, description))
        row = cursor.fetchone()
        cat_id, cat_name = row[0], row[1]
        category_map[cat_name] = cat_id
        if copy_category_image(cat_id, idx, cursor):
            category_images_loaded += 1
    print(f"  {len(category_map)} categories ready.")
    print(f"  {category_images_loaded} category images loaded.")

    # 2. Insert products
    print("Loading products ...")
    products_loaded = 0
    images_loaded = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = int(row["product_id"])
            cat_name = PRODUCT_CATEGORY.get(pid)
            cat_id = category_map.get(cat_name) if cat_name else None

            cursor.execute(INSERT_PRODUCT_SQL, (
                pid,
                row["product_name"].strip(),
                float(row["mrp"]),
                parse_bool(row["Is_discontinued"]),
                row["manufacturer_name"].strip(),
                row["pack_size_label"].strip(),
                row.get("short_composition1", "").strip(),
                row.get("short_composition2", "").strip(),
                cat_id,
                pid in NEW_LAUNCH_IDS,
                pid in TRENDING_IDS,
                pid in SPOTLIGHT_IDS,
                False,
            ))
            products_loaded += 1
            images_loaded += copy_images(pid, cursor)

    # 3. Load product features
    features_loaded = 0
    if FEATURES_CSV_FILE.exists():
        print("Loading product features ...")
        with open(FEATURES_CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = int(row["product_id"])
                cursor.execute(INSERT_FEATURE_SQL, (
                    pid,
                    row.get("description", "").strip(),
                    row.get("uses", "").strip(),
                    row.get("benefits", "").strip(),
                    row.get("side_effects", "").strip(),
                    row.get("how_to_use", "").strip(),
                    row.get("substitutes", "").strip(),
                ))
                features_loaded += 1
        print(f"  {features_loaded} product features loaded.")
    else:
        print(f"WARNING: Features CSV not found at {FEATURES_CSV_FILE}, skipping.")

    # 4. Update category product counts
    print("Updating category product counts ...")
    cursor.execute(UPDATE_CATEGORY_COUNT_SQL)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nDone.")
    print(f"  Products loaded  : {products_loaded}")
    print(f"  Images loaded    : {images_loaded}")
    print(f"  Features loaded  : {features_loaded}")
    print(f"\nCategories assigned:")
    from collections import Counter
    counts = Counter(PRODUCT_CATEGORY.values())
    for cat, count in sorted(counts.items()):
        print(f"  {cat:<30} {count} products")


if __name__ == "__main__":
    main()
