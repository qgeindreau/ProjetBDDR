# Generated by Django 3.1.7 on 2021-04-20 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recherche', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='Mad',
            field=models.DateTimeField(blank=True, default=''),
        ),
    ]
