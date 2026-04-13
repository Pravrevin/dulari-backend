from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_category_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="count_of_products",
            field=models.IntegerField(default=0),
        ),
    ]
