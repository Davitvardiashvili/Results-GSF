# Generated by Django 4.2.7 on 2023-11-19 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_remove_cart_stage_group_cart_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='place',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
