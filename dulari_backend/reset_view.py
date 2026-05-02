"""
reset_view.py
-------------
POST /api/admin/reset-and-load/

Drops the public schema, re-runs all migrations, clears media sub-directories,
then runs every seed-loading script under scripts/ in order.

Disabled when DEBUG=False to prevent accidental destructive use.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import psycopg2
from decouple import config

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


BACKEND_DIR = Path(settings.BASE_DIR)
SCRIPTS_DIR = BACKEND_DIR / "scripts"

LOAD_SCRIPTS = [
    "load_data.py",
    "load_deals.py",
    "load_super_saving_deals.py",
    "load_combos.py",
    "load_generic_medicine.py",
]

MEDIA_SUBDIRS = ["products", "categories", "generic_medicines"]


def _drop_and_recreate_schema():
    db = settings.DATABASES["default"]
    conn = psycopg2.connect(
        dbname=db["NAME"],
        user=db["USER"],
        password=db["PASSWORD"],
        host=db["HOST"],
        port=db["PORT"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute(f'GRANT ALL ON SCHEMA public TO "{db["USER"]}";')
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    cur.close()
    conn.close()


def _clear_media():
    for sub in MEDIA_SUBDIRS:
        path = BACKEND_DIR / "media" / sub
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def _run_load_script(name: str) -> dict:
    script = SCRIPTS_DIR / name
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_DIR),
        timeout=600,
    )
    return {
        "script": name,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-1500:],
        "stderr_tail": proc.stderr[-1500:],
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_and_load(request):
    expected_token = config("ADMIN_RESET_TOKEN", default="")
    provided_token = request.headers.get("X-Admin-Token", "")
    if not expected_token or provided_token != expected_token:
        return Response(
            {"detail": "Forbidden: invalid or missing X-Admin-Token header."},
            status=status.HTTP_403_FORBIDDEN,
        )

    log = []

    for alias in connections:
        connections[alias].close()

    try:
        _drop_and_recreate_schema()
        log.append("dropped and recreated public schema")
    except Exception as e:
        return Response(
            {"detail": f"Schema reset failed: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    _clear_media()
    log.append("cleared media sub-directories: " + ", ".join(MEDIA_SUBDIRS))

    try:
        call_command("migrate", verbosity=0, interactive=False)
        log.append("applied all migrations")
    except Exception as e:
        return Response(
            {"detail": f"Migrate failed: {e}", "log": log},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    script_results = []
    for name in LOAD_SCRIPTS:
        result = _run_load_script(name)
        script_results.append(result)
        if result["returncode"] != 0:
            return Response(
                {
                    "detail": f"Load script {name} failed",
                    "log": log,
                    "script_results": script_results,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        {
            "detail": "Database reset and reloaded successfully.",
            "log": log,
            "scripts_run": [r["script"] for r in script_results],
            "script_results": script_results,
        }
    )
