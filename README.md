# brs5-energy
Personal energy tracking project building on existing modules for Huawei solar panels and BE energy meter

## Architecture

The project consists of a few components hosted in different places, for the purpose of collecting data, processing data, or displaying data:

* `solar_modbus.py`: collects live information from Huawei Sun2000, via its modbus interface through TCP. Needs to be on the "dedicated" Wi-Fi network on the Sun2000 to ensure "local" connectivity. That, or on the Wi-Fi network the Sun2000 connects to, but that is untested and supposedly less reliable.
  In our setup, this is a component running on the same device as Home Assistant (`hassio`), as that is connected to our home network via LAN, but connected to the Sun2000's wireless network via Wi-Fi.
* `dsmr.py`: collects live information from the BE Fluvius meter. Through ...
