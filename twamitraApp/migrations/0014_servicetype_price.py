# Generated by Django 4.2.5 on 2023-12-30 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twamitraApp', '0013_corporatedb_address_corporatedb_alternatephone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
