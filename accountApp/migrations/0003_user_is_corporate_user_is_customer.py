# Generated by Django 4.2.5 on 2023-12-24 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountApp', '0002_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_corporate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
    ]
