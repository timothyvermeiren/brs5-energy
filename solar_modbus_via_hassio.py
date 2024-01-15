import datetime, os, sys, time, traceback
import psycopg2
from dotenv import load_dotenv

import postgres

load_dotenv()

# Note that this module is currently not in use due to a conflict with Home Assistant. When both try to connect to the Solar Inverter modbus interface, only one is able to actually read the data. This module is preserved for potential future use, but it's no longer run as a service. Instead, the BRS5 Energy web application displays data from Home Assistant's postgres output/recorder.

# pg_connection is the connection to the BRS5 Energy database itself.
pg_connection = postgres.connect()

# pg_connection_hassio is the connection to hassio which captures the modbus_solar data "for us".
try:
    pg_connection_hassio = psycopg2.connect(
        host=os.environ["hassio_recorder_pg_host"],
        port=os.environ["hassio_recorder_pg_port"],
        database=os.environ["hassio_recorder_pg_database"],
        user=os.environ["hassio_recorder_pg_username"],
        password=os.environ["hassio_recorder_pg_password"]
    )
    pg_connection_hassio.autocommit = True
    print(f"Successfully connected to postgres database on Hassio.")
except Exception as e:
    print(f"Unable to connect to postgres database on hassio:\n\t{e}\n\t{traceback.format_exc()}")
    sys.exit()


while True:

    print("-")
    print(f"{ datetime.datetime.utcnow() }")
        
    try:

        # Determine the most recent measurement we already logged to then incrementally get new data.
        pg_cursor = pg_connection.cursor()
        pg_max_timestamp_query = f"SELECT MAX(record_timestamp) FROM { os.environ['pg_raw_table'] } WHERE source = 'solar_modbus_via_hassio' AND metric = 'Input Power';"
        pg_cursor.execute(pg_max_timestamp_query)
        max_timestamp = pg_cursor.fetchone()[0]

        # Build query for hassio recorder data after that timestamp
        postgres_hassio_query_for_input_power = f"""
        select
            to_timestamp(s.last_updated_ts) as record_timestamp, 
            sa.shared_attrs::jsonb ->> 'unit_of_measurement' as unit,
            case s.state when 'unavailable' then 0::float when 'unknown' then 0::float else s.state::float end as value
            -- sm.*,
            -- s.*,
            -- sa.*
        from public.states_meta sm
            inner join public.states s on sm.metadata_id = s.metadata_id
            inner join public.state_attributes sa on s.attributes_id = sa.attributes_id 
        where sm.entity_id = 'sensor.inverter_active_power'
            and to_timestamp(last_updated_ts) > '{ max_timestamp }'
        order by last_updated_ts ASC
        """
        
        # Execute said query to get the data
        pg_hassio_cursor = pg_connection_hassio.cursor()
        pg_hassio_cursor.execute(postgres_hassio_query_for_input_power)

        new_input_power_data = pg_hassio_cursor.fetchall()

        if len(new_input_power_data) > 0:
            for input_power_row in new_input_power_data:

                data_point_value = input_power_row[2]
                data_point_unit = input_power_row[1]
                print(f"Input power: { data_point_value } { data_point_unit }")

                # Write to Postgres
                postgres.log_data(pg_connection, table=os.environ["pg_raw_table"], source="solar_modbus_via_hassio", metric="Input Power", value=data_point_value, unit=data_point_unit)
        else:
            print(f"No data read.")
            # Writing zeros as a test. Don't do this in "production" as this skews the max timestamp we use to read data incrementally!
            # postgres.log_data(pg_connection, table=os.environ["pg_raw_table"], source="solar_modbus_via_hassio", metric="Input Power", value=0, unit="W")

    except Exception as e:

        print(f"Unable to read solar inverter modbus data from Hassio recorder data:\n\t{e}\n\t{traceback.format_exc()}")

    time.sleep(2)
