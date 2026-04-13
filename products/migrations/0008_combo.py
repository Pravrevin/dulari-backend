from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0007_supersavingdeal_product_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="Combo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("combo_name", models.CharField(max_length=255)),
                (
                    "product1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="combos_as_product1",
                        to="products.product",
                    ),
                ),
                (
                    "product2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="combos_as_product2",
                        to="products.product",
                    ),
                ),
                ("tags", models.JSONField(default=list, help_text="List of tag strings e.g. ['pain_relief', 'fever']")),
                ("combo_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "products_combo",
                "ordering": ["combo_name"],
            },
        ),
    ]
