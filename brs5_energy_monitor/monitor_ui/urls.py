from django.urls import path

from . import views

app_name = "monitor_ui"
urlpatterns = [
    path("", views.index, name="index"),
    path("getMonitorValues/", views.get_monitor_values_async, name="get_monitor_values_async"),
]
