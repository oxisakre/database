# Generated by Django 3.2.5 on 2024-08-12 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_analysis', '0007_alter_customer_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='product',
            name='created_at',
        ),
    ]
