# Generated by Django 3.2.5 on 2024-08-23 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_analysis', '0016_order_canmerkung'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]