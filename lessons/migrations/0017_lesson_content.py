# Generated by Django 3.0 on 2020-01-18 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0016_lesson_references'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
