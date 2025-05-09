# Generated by Django 4.2.7 on 2024-06-24 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_ui', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solarplant',
            name='kwp',
            field=models.DecimalField(decimal_places=7, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='solarplant',
            name='latitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
        migrations.AlterField(
            model_name='solarplant',
            name='longitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
    ]
