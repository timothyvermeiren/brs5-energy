from sun2000_modbus import inverter
from sun2000_modbus import registers
from pymodbus.exceptions import ConnectionException

import datetime, os, sys, time, traceback
import psycopg2
from dotenv import load_dotenv

import postgres

load_dotenv()

# Note that this module is currently not in use due to a conflict with Home Assistant. When both try to connect to the Solar Inverter modbus interface, only one is able to actually read the data. This module is preserved for potential future use, but it's no longer run as a service. Instead, the BRS5 Energy web application displays data from Home Assistant's postgres output/recorder.

pg_connection = postgres.connect()

try:
    inverter = inverter.Sun2000(host=os.environ["inverter_ip"], port=os.environ["inverter_port"])
    inverter.connect()
    if not inverter.isConnected():
        raise Exception("Could not connect to solar inverter modbus, for... reasons.")
    print("Successfully connected to solar inverter modbus.")
except Exception as e:
    print(f"Unable to connect to solar inverter modbus:\n\t{e}\n\t{traceback.format_exc()}")
    sys.exit()

while True:

    print("-")
    print(f"{ datetime.datetime.utcnow() }")
        
    try:

        input_power = inverter.read_formatted(registers.InverterEquipmentRegister.InputPower)

        if input_power is not None:

            data_point_value = float(input_power.split(" ")[0])
            data_point_unit = input_power.split(" ")[1]
            print(f"Input power: { input_power }")

            # Write to Postgres
            postgres.log_data(pg_connection, table=os.environ["pg_raw_table"], source="solar_modbus", metric="Input Power", value=data_point_value, unit=data_point_unit)
        else:
            print(f"No data read.")

    except Exception as e:

        print(f"Unable to read solar inverter modbus data:\n\t{e}\n\t{traceback.format_exc()}")

        # Could be that we were asking too much. Wait a bit, reconnect, continue.
        if type(e) in [ConnectionException, ValueError]:
            print("Seems like this was due to our connection being worn out. Let's wait a few seconds and reconnect.")
            time.sleep(5)
            inverter.connect()

    time.sleep(2)
