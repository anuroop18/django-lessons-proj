# Generated by Django 3.0.6 on 2020-05-23 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0023_similarlesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stripe_product_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
