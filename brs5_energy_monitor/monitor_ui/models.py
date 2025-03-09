from django.db import models
from django.conf import settings

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

class SolarPlant(models.Model):
    """
    "Properties" for Forecast.Solar which contain a plant's coordinates, declination, and azimuth, for retrieval.
    """
    owner = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.TextField()
    # The next 4 fields are purely based on the values needed for Forecast.Solar: https://doc.forecast.solar
    latitude = models.DecimalField(decimal_places=7, max_digits=10)
    longitude = models.DecimalField(decimal_places=7, max_digits=10)
    declination = models.IntegerField()
    azimuth = models.IntegerField()
    kwp = models.DecimalField(decimal_places=7, max_digits=10, default=0)

    class Meta:
        db_table = 'solar_plant'


class SolarForecast(models.Model):
    record_timestamp = models.DateTimeField(primary_key=True)
    source = models.CharField(max_length=255)
    metric = models.CharField(max_length=255, blank=True, null=True)
    value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)
    solar_plant = models.ForeignKey(to=SolarPlant, on_delete=models.CASCADE)

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

