# Generated by Django 3.2.5 on 2024-08-14 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_analysis', '0010_remove_product_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
    ]