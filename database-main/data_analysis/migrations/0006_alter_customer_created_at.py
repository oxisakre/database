# Generated by Django 3.2.5 on 2024-08-12 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_analysis', '0005_auto_20240812_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
