import os, sys, requests, time, datetime
import psycopg2
from dotenv import load_dotenv
import argparse

import postgres

load_dotenv()

supported_modes = ["postgres_cleanup", "solar_estimate_refresh"]

# Arguments determine which job we'll perform.
parser = argparse.ArgumentParser(prog="main.py", description="Complete documentation of command-line arguments available here: https://biztory.atlassian.net/wiki/spaces/BWP/pages/20840451/Installing+Configuring+and+Running+TabMove")
parser.add_argument("--mode", "-m", dest="mode", required=True, type=str, help=f"The mode to run in which determines which job to perform. Possible values are: { ', '.join(supported_modes) }.")
args = parser.parse_args()
mode = args.mode.lower() # Let's avoid confusion

if mode not in supported_modes:
    print(f"Mode \"{ mode }\" is not supported. Supported values are: { ', '.join(supported_modes) }")
    sys.exit(1)

pg_connection = postgres.connect()
pg_cursor = pg_connection.cursor()

# Mode "postgres_cleanup": clean-up of raw records older than 48 hours.
if mode == "postgres_cleanup":
    pg_delete_query = f"DELETE FROM { os.environ['pg_raw_table'] } WHERE record_timestamp < NOW() - interval '48 hours'"
    print(f"Clean-up of raw records with query:\n\t{ pg_delete_query }")
    pg_cursor.execute(pg_delete_query)
    print(f"{ pg_cursor.rowcount } rows deleted.")
    pg_connection.commit()

# Mode "solar_estimate_refresh": updates solar energy production estimates from (source TBD)
if mode == "solar_estimate_refresh":
    
    print("Refreshing solar production estimates from solar.io or umh forecast.solar.")
    if "fc_solar_api_key" in os.environ and os.environ["fc_solar_api_key"] is not None:
        fc_solar_api_key = f"{ os.environ['fc_solar_api_key'] }/"

    # Get solar plants, raw, no Django, it's a lot of trouble to get that to work in here "through" Django
    pg_select_solar_plants_query = f"SELECT * FROM { os.environ['pg_solar_plants_table'] }"
    pg_cursor.execute(pg_select_solar_plants_query)
    solar_plants_raw = pg_cursor.fetchall()
    solar_plants = []
    for solar_plant_raw in solar_plants_raw:
        solar_plants.append({
            "id": solar_plant_raw[0],
            "name": solar_plant_raw[1],
            "latitude": solar_plant_raw[2],
            "longitude": solar_plant_raw[3],
            "declination": solar_plant_raw[4],
            "azimuth": solar_plant_raw[5],
            "owner_id": solar_plant_raw[6],
            "kwp": solar_plant_raw[7],
        })

    # Mapping of what we will get
    fc_solar_data_mapping = {
        "watts": {
            "metric_label": "Watts (power) average for the period",
            "unit": "W"
        },
        "watt_hours_period": {
            "metric_label": "Watt hours (energy) for the period",
            "unit": "W h"
        },
        "watt_hours": {
            "metric_label": "Cumulative Watt hours (energy) throuhgout the day, per hour",
            "unit": "W h"
        },
        "watt_hours_day": {
            "metric_label": "Total Watt hours (energy) for the day",
            "unit": "W h"
        }
    }

    for solar_plant in solar_plants:

        # https://api.forecast.solar/:apikey/estimate/:lat/:lon/:dec/:az/:kwp
        fc_solar_url = f"https://api.forecast.solar/{fc_solar_api_key}estimate/{solar_plant['latitude']}/{solar_plant['longitude']}/{solar_plant['declination']}/{solar_plant['azimuth']}/{solar_plant['kwp']}"
        fc_solar_response = requests.get(url=fc_solar_url, headers={ "Accept": "application/json" })

        if not fc_solar_response.ok:
            print(f"Something went wrong getting the solar production estimate data from forecast.solar:\n\t{ fc_solar_response.text }")

        else:
            print("Response received from forecast.solar; storing in Postgres after clearing the table.")
            pg_delete_query = f"DELETE FROM { os.environ['pg_forecast_table'] } WHERE solar_plant = { solar_plant['id'] }"
            pg_cursor.execute(pg_delete_query)
            print(f"{ pg_cursor.rowcount } rows deleted.")
            pg_connection.commit()

            solar_forecast_data = fc_solar_response.json()
            solar_forecast_request_timestamp = solar_forecast_data.get("message", {}).get("info", {}).get("time_utc", "")
            
            for metric in solar_forecast_data.get("result", {}).keys():
                print(f"Processing metric: { metric }")
                rows_for_insertion = [] # We're going to put these in the right order for our table, then execute_many
                for datapoint_key, datapoint_value in solar_forecast_data.get("result", {}).get(metric, []).items():
                    rows_for_insertion.append([
                        datapoint_key, # "record_timestamp"
                        "forescast.solar", # "source"
                        fc_solar_data_mapping[metric].get("metric_label", metric), # "metric"
                        datapoint_value, # "value"
                        fc_solar_data_mapping[metric].get("unit", "W"), # "unit"
                        solar_plant['id'] # "solar_plant_id" i.e. its ID
                    ])
                pg_cursor.executemany(f"INSERT INTO { os.environ['pg_forecast_table'] } VALUES(%s, %s, %s, %s, %s, %s)", rows_for_insertion)
                pg_connection.commit()
                print(f"\t{ pg_cursor.rowcount } rows inserted into { os.environ['pg_forecast_table'] }.")

pg_connection.close()

print("We're done!")