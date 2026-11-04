import os
import urllib.parse
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

SERVER = os.getenv("SQL_SERVER", "localhost")
DATABASE = os.getenv("OLTP_DATABASE", "LicentaDWH_OLTP")
DRIVER = os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_RAW_PATH = PROJECT_ROOT / "data" / "source_raw"

# Load parent tables before child tables to preserve foreign-key integrity.
TABLES_IN_LOAD_ORDER = [
    "categories",
    "stores",
    "customers",
    "products",
    "orders",
    "order_items",
]

# Delete child tables before parent tables when reloading the dataset.
DELETE_STATEMENTS = [
    "DELETE FROM oltp.OrderItems",
    "DELETE FROM oltp.Orders",
    "DELETE FROM oltp.Products",
    "DELETE FROM oltp.Customers",
    "DELETE FROM oltp.Categories",
    "DELETE FROM oltp.Stores",
]


def get_engine():
    connection_string = urllib.parse.quote_plus(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")


def main():
    engine = get_engine()

    with engine.begin() as connection:
        print("Starting CSV -> OLTP load...")

        for statement in DELETE_STATEMENTS:
            connection.execute(text(statement))

        for table_name in TABLES_IN_LOAD_ORDER:
            csv_path = SOURCE_RAW_PATH / f"{table_name}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing source file: {csv_path}")

            dataframe = pd.read_csv(csv_path)
            dataframe.to_sql(
                name={"order_items": "OrderItems"}.get(table_name, table_name.title()),
                con=connection,
                schema="oltp",
                if_exists="append",
                index=False,
                chunksize=1000,
            )
            print(f"Loaded {len(dataframe):,} rows from {csv_path.name}.")

        print("CSV -> OLTP load completed successfully.")


if __name__ == "__main__":
    main()
