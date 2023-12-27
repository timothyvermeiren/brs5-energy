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

class SolarForecast(models.Model):
    record_timestamp = models.DateTimeField(primary_key=True)
    source = models.CharField(max_length=255)
    metric = models.CharField(max_length=255, blank=True, null=True)
    value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solar_forecast'

class GasConsumption(models.Model):
    record_timestamp = models.DateTimeField(primary_key=True)
    previous_timestamp = models.DateTimeField()
    time_interval = models.CharField(max_length=255)
    time_seconds = models.IntegerField()
    source = models.CharField(max_length=255)
    metric = models.CharField(max_length=255, blank=True, null=True)
    value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    total_consumption = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    consumption_m3_per_h = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'er_gas_consumption'

