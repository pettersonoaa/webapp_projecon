# Generated by Django 3.0 on 2020-04-22 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20200417_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='io_type',
            field=models.CharField(choices=[('in', 'in'), ('out', 'out')], max_length=3),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='io_type',
            field=models.CharField(choices=[('in', 'in'), ('out', 'out')], max_length=3),
        ),
    ]
