from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0011_genericmedicine"),
    ]

    operations = [
        migrations.AddField(
            model_name="genericmedicine",
            name="discount_percentage",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Discount % compared to the linked branded product MRP. "
                          "Formula: ((product.mrp - generic.mrp) / product.mrp) * 100",
                max_digits=5,
            ),
        ),
    ]
