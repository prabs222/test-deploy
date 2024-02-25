# Generated by Django 5.0.1 on 2024-02-25 13:09

import django.core.validators
import twamitraApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twamitraApp', '0022_alter_corporatedb_profilepic'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatedb',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='loandetail',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userdb',
            name='profilePic',
            field=models.ImageField(default='userDefault.svg', null=True, upload_to=twamitraApp.models.user_profile_pic_path),
        ),
    ]