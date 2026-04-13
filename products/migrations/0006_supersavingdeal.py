from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_dealoftheday"),
    ]

    operations = [
        migrations.CreateModel(
            name="SuperSavingDeal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("discount_percentage", models.DecimalField(decimal_places=2, max_digits=5, help_text="Discount percentage e.g. 30.00 for 30%")),
                ("discounted_price", models.DecimalField(decimal_places=2, max_digits=10, help_text="Price after applying the discount")),
                ("is_active", models.BooleanField(default=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="super_saving_deals",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "db_table": "products_supersavingdeal",
                "ordering": ["-discount_percentage"],
            },
        ),
    ]
