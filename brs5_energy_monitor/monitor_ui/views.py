from django.shortcuts import render
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse

from copy import deepcopy
import json

from .models import EnergyRaw, GasConsumption, SolarForecast

# Helper function to get values which we might as well just leave here. Returns a dict that we can use as the context

def get_monitor_values(include_history:bool=False) -> dict:
    
    # For all three, we create a dict (instanct.__dict__) and work with that instead of the object.
    productie_current_o = EnergyRaw.objects.filter(metric="Input Power").latest("record_timestamp")
    productie_current = model_to_dict(productie_current_o)
    if productie_current["unit"] == "W":
        # We normally capture this in W, but let's convert to kW
        productie_current["value"] = productie_current["value"] / 1000
        productie_current["unit"] = "kW"
        # TBD whether this has any impact on performance; we're manipulating the ORM representation of the data after all, perhaps we need a copy
    # For productie, we also include solar capacity to determine how much we're producing as a % of the total capacity.
    solar_capacity_total = settings.SOLAR_STRING_CAPACITY_KW
    afname_current_o = EnergyRaw.objects.filter(metric="Afgenomen ogenblikkelijk vermogen").latest("record_timestamp")
    afname_current = model_to_dict(afname_current_o)
    injectie_current_o = EnergyRaw.objects.filter(metric="Geïnjecteerd ogenblikkelijk vermogen").latest("record_timestamp")
    injectie_current = model_to_dict(injectie_current_o)
    gas_consumption_current_o = GasConsumption.objects.latest("record_timestamp")
    gas_consumption_current = model_to_dict(gas_consumption_current_o)
    ev_battery_capacity_current_o = EnergyRaw.objects.filter(metric="EV9 Battery Level").latest("record_timestamp")
    ev_battery_capacity_current = model_to_dict(ev_battery_capacity_current_o)

    # Now, determine our effective "performance", verbruik and resultaat.
    verbruik_current = {
        "value": 0,
        "unit": "kW",
        "record_timestamp": None
    }

    resultaat_current = {
        "value": 0,
        "unit": "kW",
        "label": " N/A",
        "record_timestamp": None
    }

    if float(injectie_current["value"]) > 0:
        verbruik_current["value"] = round(float(productie_current["value"]) - float(injectie_current["value"]), 3)
        resultaat_current["value"] = injectie_current["value"]
        resultaat_current["label"] = "Injectie"
        resultaat_current["record_timestamp"] = injectie_current["record_timestamp"] # It doesn't _really_ matter which time stamp we pick?
        verbruik_current["record_timestamp"] = injectie_current["record_timestamp"]
    else:
        verbruik_current["value"] = round(float(afname_current["value"]) + float(productie_current["value"]), 3)
        resultaat_current["value"] = -afname_current["value"]
        resultaat_current["label"] = "Afname"
        resultaat_current["record_timestamp"] = afname_current["record_timestamp"] # It doesn't _really_ matter which time stamp we pick?
        verbruik_current["record_timestamp"] = afname_current["record_timestamp"]
    
    # If we include history: same steps as above, more or less, but... with more data.
    verbruik_history = []
    resultaat_history = []
    gas_consumption_history = []
    solar_forecast = []
    solar_forecast_daily_wh = []

    if include_history:

        # For electricity, because we have frequent measurements, we won't load the full history; approximately 10 minutes should do?
        history_length = 600

        productie_history_o = EnergyRaw.objects.filter(metric="Input Power").order_by("-record_timestamp")[:history_length:-1]
        productie_history = list(map(model_to_dict, productie_history_o))
        for productie_history_value in productie_history:
            if productie_history_value["unit"] == "W":
                # We normally capture this in W, but let's convert to kW
                productie_history_value["value"] = productie_history_value["value"] / 1000
                productie_history_value["unit"] = "kW"
        afname_history_o = EnergyRaw.objects.filter(metric="Afgenomen ogenblikkelijk vermogen").order_by("-record_timestamp")[:history_length:-1]
        afname_history = list(map(model_to_dict, afname_history_o))
        injectie_history_o = EnergyRaw.objects.filter(metric="Geïnjecteerd ogenblikkelijk vermogen").order_by("-record_timestamp")[:history_length:-1]
        injectie_history = list(map(model_to_dict, injectie_history_o))

        for i in range(history_length):
            # Prepare, add the current values as a template
            verbruik_history.append(deepcopy(verbruik_current))
            resultaat_history.append(deepcopy(resultaat_current))
            # Update
            if float(injectie_current["value"]) > 0:
                verbruik_history[i]["value"] = round(float(productie_history[i]["value"]) - float(injectie_history[i]["value"]), 3)
                resultaat_history[i]["value"] = injectie_history[i]["value"]
                resultaat_history[i]["label"] = "Injectie"
                resultaat_history[i]["record_timestamp"] = injectie_history[i]["record_timestamp"] # It doesn't _really_ matter which time stamp we pick?
                verbruik_history[i]["record_timestamp"] = injectie_history[i]["record_timestamp"]
            else:
                verbruik_history[i]["value"] = round(float(afname_history[i]["value"]) + float(productie_history[i]["value"]), 3)
                resultaat_history[i]["value"] = -afname_history[i]["value"]
                resultaat_history[i]["label"] = "Afname"
                resultaat_history[i]["record_timestamp"] = afname_history[i]["record_timestamp"] # It doesn't _really_ matter which time stamp we pick?
                verbruik_history[i]["record_timestamp"] = afname_history[i]["record_timestamp"]

        # For gas, there is no need for history_length (there are fewer measurements), but because it comes from a different pre-processed view we need to also rearrange and prepare.
        gas_consumption_o = GasConsumption.objects.order_by("record_timestamp")
        gas_consumption_history = list(map(model_to_dict, gas_consumption_o))
        # for i in range(len(gas_consumption)):
        #     # Current values as a template
        #     gas_consumption_history.append(gas_consumption_current)
        #     gas_consumption_history[i]["record_timestamp"] = gas_consumption[i]["record_timestamp"]


        # We will consider the forecast as part of "history" as well; mainly because this is just used to determine which data to get with the initial load, as opposed to subsequent async calls that just have updated data.
        solar_forecast_o = SolarForecast.objects.filter(metric="Watt hours (energy) for the period").order_by("record_timestamp")
        solar_forecast = list(map(model_to_dict, solar_forecast_o))
        solar_forecast_daily_wh_o = SolarForecast.objects.filter(metric="Total Watt hours (energy) for the day").order_by("record_timestamp")
        solar_forecast_daily_wh = list(map(model_to_dict, solar_forecast_daily_wh_o))
    

    return {
        "productie_current": productie_current,
        "solar_capacity_total": solar_capacity_total,
        "productie_pct_capacity": round(float(productie_current["value"]) / float(solar_capacity_total), 2),
        "afname_current": afname_current,
        "injectie_current": injectie_current,
        "verbruik_current": verbruik_current,
        "resultaat_current": resultaat_current,
        "gas_consumption_current": gas_consumption_current,
        "verbruik_history": json.dumps(verbruik_history, default=str),
        "resultaat_history": json.dumps(resultaat_history, default=str),
        "gas_consumption_history": json.dumps(gas_consumption_history, default=str),
        "ev_battery_capacity_current": ev_battery_capacity_current,
        "solar_forecast": json.dumps(solar_forecast, default=str),
        "solar_forecast_daily_wh": solar_forecast_daily_wh,
    }

# Create your views here.

def index(request):
    context = get_monitor_values(include_history=True)
    return render(request, "monitor.html", context)


def get_monitor_values_async(request):
    try:
        monitor_values = get_monitor_values()
        return JsonResponse(monitor_values)
    except Exception as e:
        print(e)