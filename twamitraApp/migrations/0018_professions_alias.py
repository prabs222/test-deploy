# Generated by Django 5.0.1 on 2024-01-21 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twamitraApp', '0017_generatedcode_expiration_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='professions',
            name='alias',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]