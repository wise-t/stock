# Generated by Django 3.2.4 on 2024-06-21 09:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stockapp', '0004_alter_product_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateField(default=datetime.datetime(2024, 6, 21, 9, 35, 34, 597793, tzinfo=utc)),
        ),
    ]