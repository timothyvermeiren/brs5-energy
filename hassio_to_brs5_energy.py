import datetime, os, sys, time, traceback
import psycopg2
from dotenv import load_dotenv

import postgres

load_dotenv()

# pg_connection is the connection to the BRS5 Energy database itself.
pg_connection = postgres.connect()

# pg_connection_hassio is the connection to hassio which captures the modbus_solar and other data "for us".
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

hassio_data_to_fetch = {
    "solar_modbus": { 
        "source": "solar_modbus_via_hassio",
        "metric": "Input Power",
        "entity_id": "sensor.inverter_active_power"
     },
    "ev9_battery_level": { 
        "source": "ev",
        "metric": "EV9 Battery Level",
        "entity_id": "sensor.ev9_ev_battery_level"
     }
}

while True:

    print("-")
    print(f"{ datetime.datetime.utcnow() }")

    for hassio_data in hassio_data_to_fetch.keys():

        print(f"Reading { hassio_data } from hassio.")
        
        try:

            # Determine the most recent measurement we already logged to then incrementally get new data.
            pg_cursor = pg_connection.cursor()
            pg_max_timestamp_query = f"SELECT MAX(record_timestamp) FROM { os.environ['pg_raw_table'] } WHERE source = '{ hassio_data_to_fetch[hassio_data]['source'] }' AND metric = '{ hassio_data_to_fetch[hassio_data]['metric'] }';"
            pg_cursor.execute(pg_max_timestamp_query)
            max_timestamp = pg_cursor.fetchone()[0]
            if max_timestamp is not None:
                max_timestamp_query_condition = f"and to_timestamp(last_updated_ts) > '{ max_timestamp }'"
                max_timestamp_query_condition_limit = ""
            else:
                # max_timestamp_query_condition = f"and to_timestamp(last_updated_ts) = (SELECT MAX(to_timestamp(last_updated_ts)) FROM states)"
                # The above did not work so well, for some reason. LIMIT will work better.
                max_timestamp_query_condition = ""
                max_timestamp_query_condition_limit = "limit 1"


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
            where sm.entity_id = '{ hassio_data_to_fetch[hassio_data]['entity_id'] }'
                { max_timestamp_query_condition }
            order by last_updated_ts ASC
            { max_timestamp_query_condition_limit }
            """
            
            # Execute said query to get the data
            pg_hassio_cursor = pg_connection_hassio.cursor()
            pg_hassio_cursor.execute(postgres_hassio_query_for_input_power)

            new_hassio_data = pg_hassio_cursor.fetchall()

            if len(new_hassio_data) > 0:
                for hassio_data_row in new_hassio_data:

                    data_point_value = hassio_data_row[2]
                    data_point_unit = hassio_data_row[1]
                    data_point_record_timestamp = hassio_data_row[0]
                    print(f"{ hassio_data_to_fetch[hassio_data]['metric'] }: { data_point_value } { data_point_unit }")

                    # Write to Postgres
                    postgres.log_data(pg_connection, table=os.environ["pg_raw_table"], source=hassio_data_to_fetch[hassio_data]['source'], metric=hassio_data_to_fetch[hassio_data]['metric'], value=data_point_value, unit=data_point_unit, record_timestamp=data_point_record_timestamp)
            else:
                print(f"No (new) data read.")
                # Writing zeros as a test. Don't do this in "production" as this skews the max timestamp we use to read data incrementally!
                # postgres.log_data(pg_connection, table=os.environ["pg_raw_tab"], source={ hassio_data_to_fetch[hassio_data]['source'], metric=hassio_data_to_fetch[hassio_data]['metric'], value=0, unit="W")

        except Exception as e:

            print(f"Unable to read { hassio_data } data from Hassio recorder data:\n\t{e}\n\t{traceback.format_exc()}")

    time.sleep(2)
