from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse

from copy import deepcopy
import json

from .models import EnergyRaw

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
    afname_current_o = EnergyRaw.objects.filter(metric="Afgenomen ogenblikkelijk vermogen").latest("record_timestamp")
    afname_current = model_to_dict(afname_current_o)
    injectie_current_o = EnergyRaw.objects.filter(metric="Geïnjecteerd ogenblikkelijk vermogen").latest("record_timestamp")
    injectie_current = model_to_dict(injectie_current_o)

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

    if include_history:

        history_length = 50

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

    
    return {
        "productie_current": productie_current,
        "afname_current": afname_current,
        "injectie_current": injectie_current,
        "verbruik_current": verbruik_current,
        "resultaat_current": resultaat_current,
        "verbruik_history": json.dumps(verbruik_history, default=str),
        "resultaat_history": json.dumps(resultaat_history, default=str),
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