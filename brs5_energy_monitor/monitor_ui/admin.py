from django.contrib import admin
from .models import EnergyRaw, GasConsumption, SolarPlant, SolarForecast

# Register your models here.

admin.site.register(SolarPlant)