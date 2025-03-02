# brs5-energy
Personal energy tracking project building on existing modules for Huawei solar panels and BE energy meter

## Architecture

The project consists of a few components hosted in different places, for the purpose of collecting data, processing data, storing data, or displaying data:

### Collecting Data 

* `solar_modbus.py`: collects **live information from Huawei Sun2000**, via its modbus interface through TCP. Needs to be on the "dedicated" Wi-Fi network on the Sun2000 to ensure "local" connectivity. That, or on the Wi-Fi network the Sun2000 connects to, but that is untested and supposedly less reliable.  
  In our setup, this is a component running on the same device as Home Assistant (`hassio`), as that is connected to our home network via LAN, but connected to the Sun2000's wireless network via Wi-Fi.
* `dsmr.py`: collects **live information from the BE Fluvius meter**, through a USB adapter for the serial port.  
  In our case, this relies on a Pi Zero connected to said USB adapter running [smartmeterBridge](https://github.com/legolasbo/smartmeterBridge), exposing it as a TCP/IP service. In turn, this module connects to _that_ TCP/IP service with `socket`.
  Note that we have to ensure our Raspberry Pi Zero 2W does not go into powersave mode, so we have a second systemd service on there to prevent that from happening (it sets `iw dev wlan0 set power_save off`) every restart.
* `fusion_solar.py`: not currently used; but could be used to get solar panel information from the **Huawei Fusion Solar API**.
* Data for solar production forecast is collected from https://forecast.solar/. As we're not doing this live but at a daily rate, this is implemented in `jobs.py` and called through `cron` instead of a separate module running as a service.

#### Running these as services

* Using the service files in `resources/systemd` or `resources/smartmeterBridge`.
* Link the file with its absolute path, e.g.: `systemctl --user link /opt/brs5-energy/resources/systemd/brs5_energy_dsmr.service`
* Then enable it: `systemctl enable /home/timothy/.config/systemd/user/brs5_energy_dsmr.service`
* Then start it: `systemctl start brs5_energy_dsmr.service`

### Storing and Processing Data

Postgres database, with DDL in `resources/postgres_setup.sql`. Relies on a few scheduled procedures to aggregate the data, TBD whether these are run natively in Postgres (pgAgent) or with `cron` + Python.

The modules above write "live" information into a raw data table, which is further manipulated by the "processing & aggregations" items below.

Note that **the postgres instance's max open file ulimit has been modified**. There are lots of long-lasting connections (from the "agents") that caused postgres to eventually stop accepting new connections after a day or two. This was due to the fact that that limit for max number of open files was reached. The following changes were applied:

* Edit the service's unit file to increase the limit. The service (in this case) is called `postgresql@12-main.service`.
* The service uses a generated unit file, so we can "access" it with: `systemctl edit --full postgresql@12-main.service`
* We set `LimitNOFILE` under `[Service]` to `4096``.

Processing & aggregations:

**To be reviewed!** There is probably a more efficient way as we might be better off simply using the same principle as energy providers and keeping 15-minute min/max/avg/sum. Or even better, read that from the meter if we can, because it might not be possible for us to accurately calculate this.

Original suggestion:

* Every **hour**: aggregates the `avg` and `sum` of the last 60 minutes or 3600 seconds of raw data. Does not delete data.
* Every **day**: aggregates the `avg` and `sum` of the last 86400 seconds of data. **Clears the raw data** from [antepenultimate](https://en.wiktionary.org/wiki/antepenultimate) day (not today, not the day before today... but the day before _that_).
* Every **week**: aggregates the `avg` and `sum` of the already-aggregated daily data of the last 7 days.
* Every **month**: aggregates the `avg` and `sum` of the already-aggregated daily data of the last 30 days.

### Displaying Data

This will be a simple Django application fetching the latest records of raw data to show live usage, in combination with aggregated data to provide context.

#### Running the Django application with Apache

And example of the virtual host to use is shown in `resources/apache/brs5-energy.duckdns.org.conf`. Note that we need to install `mod_wsgi` _for the correct Python environment_, as [shown here](https://stackoverflow.com/questions/69302698/django-mod-wsgi-apache-server-modulenotfounderror-no-module-named-django).

* `cd ~/downloads`
* `curl -O https://codeload.github.com/GrahamDumpleton/mod_wsgi/tar.gz/4.9.4`
* `tar -xf 4.9.4`
* `cd mod_wsgi-4.9.4/`
* Make sure we have apxs2 for the next step: `sudo apt-get install apache2-dev`
* Then this is key: `./configure --with-python=/opt/brs5-energy/.venv/bin/python3.10`
* `make`
* `sudo make install`

Then, configure Apache with the virtual host and restart:

* `sudo a2ensite brs5-energy.duckdns.org`
* `sudo systemctl restart apache2`

To make changes, we do need to reload apache before they appear. That's fine.

To configure TLS encryption with certbot, we do need to do something slightly different regarding the fact that we're using WSGI here. Relevant [answer on SO](https://stackoverflow.com/questions/51322329/apache-with-ssl-configuration-not-working-with-wsgi-configuration-for-django-app).

* Comment out the `WSGIDaemonProcess` line first (in the non-HTTPS conf).
* Run `sudo certbot --apache -d brs5-energy.duckdns.org`.
* Un-comment the line from before.
