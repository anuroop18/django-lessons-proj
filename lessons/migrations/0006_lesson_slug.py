# Generated by Django 3.0 on 2019-12-23 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_auto_20191221_0616'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
