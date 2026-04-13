from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_supersavingdeal"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supersavingdeal",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="super_saving_deal",
                to="products.product",
            ),
        ),
    ]
