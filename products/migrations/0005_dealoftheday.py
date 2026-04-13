from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_category_count_of_products"),
    ]

    operations = [
        migrations.CreateModel(
            name="DealOfTheDay",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("discount_percentage", models.DecimalField(decimal_places=2, max_digits=5, help_text="Discount percentage e.g. 20.00 for 20%")),
                ("discounted_price", models.DecimalField(decimal_places=2, max_digits=10, help_text="Price after applying discount")),
                ("offer_ends_at", models.DateTimeField(help_text="Date and time when the offer expires")),
                ("is_active", models.BooleanField(default=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deals",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "db_table": "products_dealoftheday",
                "ordering": ["offer_ends_at"],
            },
        ),
    ]
