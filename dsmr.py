import socket, select, datetime, re, os, sys, json, time, traceback
import psycopg2
from dotenv import load_dotenv

import postgres

load_dotenv()

pg_connection = postgres.connect()

try:
    dsmr_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ip = socket.gethostbyname(os.environ["dsmr_ip"])
    port = int(os.environ["dsmr_port"])
    address = (ip, port)
    # client.setblocking(False) # This was suggested somewhere, but didn't seem to work
    dsmr_client.connect(address)
    print("Successfully connected to DSMR.")
except Exception as e:
    print(f"Unable to connect to DSMR:\n\t{e}")
    sys.exit()

try:
    with open("resources/dsmr/dsmr_code_mapping.json") as f:
         dsmr_code_mapping = json.load(f)
    print("Loaded DSMR mapping.")
except Exception as e:
    print(f"Unable to load DSMR mapping:\n\t{e}")
    sys.exit()         

# Let's not always log everything... It's nice to keep the mapping as it is, but we can filter which codes we effectively want to log to the database here, to keep it a bit lighter.
active_codes = ["1.7.0", "2.7.0", "24.2.3"]

dsmr_codes_for_logging = [code for code in dsmr_code_mapping if code in active_codes]

while True:

    print("-")
    print(f"{ datetime.datetime.utcnow() }")
    ready = select.select([dsmr_client], [], [], 3) # Socket stuff

    if ready[0]:
        try:

            data = dsmr_client.recv(2048)
            data_parsed = data.decode("utf-8").split("\r\n")

            for code in dsmr_codes_for_logging:
                try:
                    
                    # Read
                    recorded_data = next((data_point for data_point in data_parsed if data_point.find(f":{code}") > 0), None)
                    if recorded_data is not None:
                        data_point_value = float(re.findall(r"\(([\d\.]+)\*", recorded_data)[0])
                        data_point_unit = re.findall(r"\*(\w+)\)$", recorded_data)[0]

                        # Write to Postgres
                        postgres.log_data(pg_connection, table=os.environ["pg_raw_table"], source="dsmr", metric=dsmr_code_mapping[code].get("label"), value=data_point_value, unit=data_point_unit)
                    else:
                        print(f"No data found for code { code }, skipping.")

                except Exception as e:
                    data_point_value = 0
                    data_point_unit = None
                    print(f"Failed to log data for code { code }.\n\t{e}\n\t{traceback.format_exc()}")
                print(f"{ dsmr_code_mapping[code]['label'] }: { data_point_value } { data_point_unit }")

        except Exception as e:
            print(f"Unable to read DSMR data:\n\t{e}\n\t{traceback.format_exc()}")
            
    else:
        print("No DSMR data read.")
    
    time.sleep(1)