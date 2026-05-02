# Generated for admin approval flow

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_alter_category_image_alter_genericmedicine_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_approved',
            field=models.BooleanField(default=False, help_text='Approved by a super admin from the admin panel'),
        ),
    ]
