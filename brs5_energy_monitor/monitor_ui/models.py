from django.db import models

# Create your models here.

# Generated with python manage.py inspectdb, based on the DDL we already had. We did manually specify record_timestamp to be the primary key.
class EnergyRaw(models.Model):
    record_timestamp = models.DateTimeField(primary_key=True)
    source = models.CharField(max_length=255)
    metric = models.CharField(max_length=255, blank=True, null=True)
    value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'energy_raw'