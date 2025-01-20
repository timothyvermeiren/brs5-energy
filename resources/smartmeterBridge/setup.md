# smartmeterBridge setup

* On Raspberry Pi Zero 2W with Raspberry Pi OS Lite
* Set up Tailscale and whatever is needed for convenient access
* Follow installation instructions from repository: https://github.com/legolasbo/smartmeterBridge
* We need the ARM64 version from Releases
* Place that in `~/smartmeter-bridge`, and create a config file there as well (see example in this folder)
* Make the binary executable: `chmod u+x smartmeter-bridge-linux-arm64`
* See the systemd configuration in this repository (`systemd/brs5_energy_smartmeter_bridge.service`) for how to ensure this is always running.
* Put a copy of this service file in `~/smartmeter-bridge`, review it, and enable it: `systemctl enable brs5_energy_smartmeter_bridge.service`
* Check the connection to this service from the DSMR Python component.