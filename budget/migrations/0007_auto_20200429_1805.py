# Generated by Django 3.0 on 2020-04-29 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_subcategory_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
