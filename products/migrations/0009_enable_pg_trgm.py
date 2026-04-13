from django.db import migrations


class Migration(migrations.Migration):
    """Enable the pg_trgm PostgreSQL extension for trigram fuzzy search."""

    dependencies = [
        ("products", "0008_combo"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        ),
    ]
