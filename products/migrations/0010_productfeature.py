from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0009_enable_pg_trgm"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductFeature",
            fields=[
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="feature",
                        serialize=False,
                        to="products.product",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Product description",
                    ),
                ),
                (
                    "uses",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Semicolon-separated list of uses",
                    ),
                ),
                (
                    "benefits",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Semicolon-separated list of benefits",
                    ),
                ),
                (
                    "side_effects",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Semicolon-separated list of side effects",
                    ),
                ),
                (
                    "how_to_use",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Instructions on how to use the product",
                    ),
                ),
                (
                    "substitutes",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Semicolon-separated list of substitute products",
                    ),
                ),
            ],
            options={
                "db_table": "products_productfeature",
            },
        ),
    ]
