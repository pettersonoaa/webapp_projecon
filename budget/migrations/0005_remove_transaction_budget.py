# Generated by Django 3.0 on 2020-04-24 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_auto_20200423_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='budget',
        ),
    ]
