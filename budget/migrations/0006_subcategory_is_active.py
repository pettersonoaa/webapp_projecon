# Generated by Django 3.0 on 2020-04-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_remove_transaction_budget'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
