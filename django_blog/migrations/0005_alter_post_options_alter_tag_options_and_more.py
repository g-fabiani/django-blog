# Generated by Django 5.0.4 on 2024-05-08 01:08

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_author'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name_plural': 'post'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name_plural': 'tag'},
        ),
        migrations.AlterModelManagers(
            name='post',
            managers=[
                ('published_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
