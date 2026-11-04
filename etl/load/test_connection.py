import os
import urllib.parse

from sqlalchemy import create_engine

SERVER = os.getenv("SQL_SERVER", "localhost")
DATABASE = os.getenv("OLTP_DATABASE", "Ecommerce_OLTP")
DRIVER = os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

connection_string = urllib.parse.quote_plus(
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

try:
    with engine.connect():
        print("Connection successful.")
except Exception as error:
    print("Connection failed.")
    print(error)
