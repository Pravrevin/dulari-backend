from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_productfeature"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenericMedicine",
            fields=[
                ("generic_product_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(help_text="Generic drug name e.g. Amoxycillin 500mg Tablet", max_length=255)),
                ("brand", models.CharField(help_text="Generic manufacturer brand name", max_length=255)),
                ("mrp", models.DecimalField(decimal_places=2, max_digits=10)),
                ("image", models.ImageField(blank=True, null=True, upload_to="generic_medicines/")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generic_medicines",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "db_table": "products_genericmedicine",
                "ordering": ["name"],
            },
        ),
    ]
