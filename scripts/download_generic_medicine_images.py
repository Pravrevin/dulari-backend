"""
download_generic_medicine_images.py
------------------------------------
Downloads one online image per medicine form-type (tablet, capsule, syrup, cream,
gel, inhaler, drops, injection, suspension, solution, expectorant) from Wikipedia
using the MediaWiki pageimages API.

Each image is saved to:
    medicine-data-picture/generic_medicine_images/{generic_product_id}/generic_{id}.jpg

Medicines of the same form share the same downloaded image (local copy per id).
Already-downloaded images are skipped on re-runs.

Usage (from dulari-backend/):
    python scripts/download_generic_medicine_images.py
"""

import csv
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CSV_FILE    = BACKEND_DIR / "medicine-data-picture" / "generic_medicine.csv"
IMAGES_DIR  = BACKEND_DIR / "medicine-data-picture" / "generic_medicine_images"

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS  = {"User-Agent": "DulariMedicalStore/1.0 (educational project; github.com/dulari)"}

# Wikipedia article that best represents each medicine form.
# Each entry is a list; the first article with a thumbnail image wins.
FORM_WIKI_ARTICLES = {
    "tablet":      ["Tablet_(pharmacy)", "Paracetamol", "Aspirin"],
    "capsule":     ["Capsule_(pharmacy)", "Amoxicillin", "Omeprazole"],
    "syrup":       ["Ambroxol", "Paracetamol", "Liquid_medication", "Oral_rehydration_therapy"],
    "cream":       ["Hydrocortisone", "Zinc_oxide", "Clotrimazole", "Ointment"],
    "gel":         ["Topical_medication", "Diclofenac", "Topical_anesthetic"],
    "inhaler":     ["Inhaler", "Salbutamol", "Asthma"],
    "drops":       ["Eye_drop", "Ciprofloxacin", "Ophthalmology"],
    "injection":   ["Injection_(medicine)", "Syringe", "Intravenous_therapy"],
    "suspension":  ["Amoxicillin/clavulanic_acid", "Amoxicillin", "Penicillin"],
    "solution":    ["Saline_(medicine)", "Glucose", "Oral_rehydration_therapy"],
    "expectorant": ["Guaifenesin", "Cough_medicine", "Bromhexine"],
}
# Backwards-compat alias used in main()
FORM_WIKI_ARTICLE = {k: v[0] for k, v in FORM_WIKI_ARTICLES.items()}


def detect_form(name: str) -> str:
    """Return the medicine form based on keywords in the generic medicine name."""
    n = name.lower()
    if "inhaler" in n:
        return "inhaler"
    if "eye" in n or "ear" in n or "drop" in n:
        return "drops"
    if "injection" in n:
        return "injection"
    if "cream" in n:
        return "cream"
    if "gel" in n:
        return "gel"
    if "syrup" in n:
        return "syrup"
    if "suspension" in n or "oral suspension" in n or "dry syrup" in n:
        return "suspension"
    if "oral solution" in n or "solution" in n:
        return "solution"
    if "expectorant" in n:
        return "expectorant"
    if "capsule" in n:
        return "capsule"
    return "tablet"


def fetch_wiki_thumbnail_url(article: str, thumb_size: int = 400) -> str | None:
    """Query Wikipedia pageimages API and return the thumbnail URL, or None."""
    params = urllib.parse.urlencode({
        "action":      "query",
        "titles":       article,
        "prop":        "pageimages",
        "format":      "json",
        "pithumbsize": thumb_size,
    })
    req = urllib.request.Request(f"{WIKI_API}?{params}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        for page in data.get("query", {}).get("pages", {}).values():
            thumb = page.get("thumbnail")
            if thumb:
                return thumb["source"]
    except Exception as exc:
        print(f"    WARN: Wikipedia API error for '{article}': {exc}")
    return None


def download_file(url: str, dest: Path) -> bool:
    """Download a URL to dest. Returns True on success."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.read())
        return True
    except Exception as exc:
        print(f"    WARN: Download failed ({url}): {exc}")
        return False


def main():
    if not CSV_FILE.exists():
        print(f"ERROR: CSV not found at {CSV_FILE}")
        sys.exit(1)

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Processing {len(rows)} generic medicines ...\n")

    # Cache: form → Path of master downloaded file
    form_master: dict[str, Path] = {}

    downloaded = 0
    reused     = 0
    skipped    = 0
    failed     = 0

    for row in rows:
        gid  = int(row["generic_product_id"])
        name = row["name"].strip()
        form = detect_form(name)

        dest_folder = IMAGES_DIR / str(gid)
        dest_file   = dest_folder / f"generic_{gid}.jpg"

        # Already on disk — skip
        if dest_file.exists():
            print(f"  [{gid:>3}] SKIP   {name[:50]}")
            skipped += 1
            continue

        dest_folder.mkdir(parents=True, exist_ok=True)

        # Reuse cached master image for this form
        if form in form_master:
            shutil.copy2(form_master[form], dest_file)
            print(f"  [{gid:>3}] REUSE  {name[:50]}  (form={form})")
            reused += 1
            continue

        # First time we see this form — try articles in priority order
        articles  = FORM_WIKI_ARTICLES.get(form, ["Tablet_(pharmacy)"])
        thumb_url = None
        used_article = None
        for article in articles:
            print(f"  [{gid:>3}] FETCH  form={form} -> {article}")
            thumb_url = fetch_wiki_thumbnail_url(article)
            if thumb_url:
                used_article = article
                break
            time.sleep(0.3)

        if thumb_url and download_file(thumb_url, dest_file):
            form_master[form] = dest_file
            print(f"         OK     saved {dest_file.name}  ({used_article})")
            downloaded += 1
            time.sleep(0.4)   # polite delay between distinct Wikipedia calls
        else:
            print(f"  [{gid:>3}] FAILED to get image for form={form} — image will be blank")
            failed += 1

    print(f"\n{'='*55}")
    print(f"  Total processed : {len(rows)}")
    print(f"  Downloaded      : {downloaded}  (one per unique form type)")
    print(f"  Reused locally  : {reused}")
    print(f"  Skipped (exist) : {skipped}")
    print(f"  Failed          : {failed}")
    print(f"\nImages saved to: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
