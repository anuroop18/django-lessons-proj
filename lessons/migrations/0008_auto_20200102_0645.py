# Generated by Django 3.0 on 2020-01-02 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0007_subscribtion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]