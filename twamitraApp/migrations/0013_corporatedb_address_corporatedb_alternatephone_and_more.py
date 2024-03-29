# Generated by Django 4.2.5 on 2023-12-30 20:53

from django.db import migrations, models
import twamitraApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('twamitraApp', '0012_corporatepayments_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatedb',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='alternatePhone',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='companyName',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='experience',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='pan',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='profilePic',
            field=models.ImageField(null=True, upload_to=twamitraApp.models.user_profile_pic_path),
        ),
        migrations.AddField(
            model_name='corporatedb',
            name='signature',
            field=models.ImageField(null=True, upload_to=twamitraApp.models.user_signature_path),
        ),
    ]
