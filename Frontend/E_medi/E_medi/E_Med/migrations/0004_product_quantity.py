# Generated by Django 4.2.3 on 2023-08-03 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('E_Med', '0003_remove_cartitem_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
