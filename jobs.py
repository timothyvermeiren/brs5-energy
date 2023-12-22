import os, sys
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
    pg_connection.close()

# Mode "solar_estimate_refresh": updates solar energy production estimates from (source TBD)
if mode == "solar_estimate_refresh":
    print("Not implemented yet.")

print("We're done!")