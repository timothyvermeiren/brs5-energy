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
    print("Refreshing solar production estimates from solar.io.")
    if "fc_solar_api_key" in os.environ and os.environ["fc_solar_api_key"] is not None:
        fc_solar_api_key = f"{ os.environ['fc_solar_api_key'] }/"
    # https://api.forecast.solar/:apikey/estimate/:lat/:lon/:dec/:az/:kwp
    fc_solar_url = f"https://api.forecast.solar/{fc_solar_api_key}estimate/{os.environ['fc_solar_lat']}/{os.environ['fc_solar_lon']}/{os.environ['fc_solar_dec']}/{os.environ['fc_solar_az']}/{os.environ['fc_solar_kwp']}"
    fc_solar_response = requests.get(url=fc_solar_url, headers={ "Accept": "application/json" })
    if not fc_solar_response.ok:
        print(f"Something went wrong getting the solar production estimate data from forecast.solar:\n\t{ fc_solar_response.text }")
    else:

        # Mapping of what we get
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

        print("Response received from forecast.solar; storing in Postgres after clearing the table.")
        pg_delete_query = f"DELETE FROM { os.environ['pg_forecast_table'] }"
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
                    fc_solar_data_mapping[metric].get("unit", "W") # "unit"
                ])
            pg_cursor.executemany(f"INSERT INTO { os.environ['pg_forecast_table'] } VALUES(%s, %s, %s, %s, %s)", rows_for_insertion)
            pg_connection.commit()
            print(f"\t{ pg_cursor.rowcount } rows inserted into { os.environ['pg_forecast_table'] }.")

pg_connection.close()

print("We're done!")