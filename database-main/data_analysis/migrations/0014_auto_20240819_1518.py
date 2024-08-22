# Generated by Django 3.2.5 on 2024-08-19 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_analysis', '0013_alter_order_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='platform',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]