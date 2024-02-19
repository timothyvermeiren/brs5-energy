import os, sys, traceback
import datetime
from typing import Tuple
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect():

    try:
        pg_connection = psycopg2.connect(
            host=os.environ["pg_host"],
            port=os.environ["pg_port"],
            database=os.environ["pg_database"],
            user=os.environ["pg_username"],
            password=os.environ["pg_password"]
        )
        print(f"Successfully connected to postgres database.")
    except Exception as e:
        print(f"Unable to connect to postgres database:\n\t{e}\n\t{traceback.format_exc()}")
        sys.exit()
    
    return pg_connection

def log_data(pg_connection, table:str, source:str, metric:str, value:float, unit:str, record_timestamp:datetime.datetime=None):

    try:
        pg_cursor = pg_connection.cursor()
        if record_timestamp is not None:
            pg_insert_query = f"INSERT INTO { table } (record_timestamp, source, metric, value, unit) VALUES ('{ record_timestamp }', '{ source }', '{ metric }', { value }, '{ unit }')"
        else:
            pg_insert_query = f"INSERT INTO { table } (source, metric, value, unit) VALUES ('{ source }', '{ metric }', { value }, '{ unit }')"
        pg_cursor.execute(pg_insert_query)
        pg_connection.commit()
        pg_cursor.execute(f"SELECT COUNT(*) FROM { table }")
        record_count = pg_cursor.fetchone()
        print(f"Data logged successfully; there are now { record_count[0] } records logged in { table }.")
    except Exception as e:
        print(f"Unable to log data to postgres database:\n\t{e}\n\t{traceback.format_exc()}")
        sys.exit()