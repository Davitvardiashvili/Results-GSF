# Generated by Django 5.0 on 2025-01-02 14:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_remove_agegroup_group_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agegroup',
            options={'ordering': ['-updated']},
        ),
        migrations.AddField(
            model_name='agegroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agegroup',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
