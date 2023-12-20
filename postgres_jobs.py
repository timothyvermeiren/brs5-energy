import os
import psycopg2
from dotenv import load_dotenv

import postgres

load_dotenv()

pg_connection = postgres.connect()
pg_cursor = pg_connection.cursor()

# Clean-up of raw records
pg_delete_query = f"DELETE FROM { os.environ['pg_raw_table'] } WHERE record_timestamp < NOW() - interval '48 hours'"
print(f"Clean-up of raw records with query:\n\t{ pg_delete_query }")
pg_cursor.execute(pg_delete_query)
pg_connection.commit()
pg_connection.close()