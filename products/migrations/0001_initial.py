from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("product_id", models.IntegerField(primary_key=True, serialize=False)),
                ("product_name", models.CharField(max_length=255)),
                ("mrp", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_discontinued", models.BooleanField(default=False)),
                ("manufacturer_name", models.CharField(max_length=255)),
                ("pack_size_label", models.CharField(max_length=255)),
                ("short_composition1", models.CharField(blank=True, default="", max_length=500)),
                ("short_composition2", models.CharField(blank=True, default="", max_length=500)),
                ("is_new_launch", models.BooleanField(default=False, help_text="Mark product as a New Launch")),
                ("is_trending_near_you", models.BooleanField(default=False, help_text="Mark product as Trending Near You")),
                ("is_in_spotlight", models.BooleanField(default=False, help_text="Mark product as In the Spotlight")),
            ],
            options={
                "db_table": "products_product",
                "ordering": ["product_id"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="products/")),
                ("alt_text", models.CharField(blank=True, max_length=255)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "db_table": "products_productimage",
            },
        ),
    ]
