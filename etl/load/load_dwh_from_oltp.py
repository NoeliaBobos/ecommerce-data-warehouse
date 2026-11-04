import os
import urllib.parse

from sqlalchemy import create_engine, text

SERVER = os.getenv("SQL_SERVER", "localhost")
OLTP_DATABASE = os.getenv("OLTP_DATABASE", "Ecommerce_OLTP")
DWH_DATABASE = os.getenv("DWH_DATABASE", "Ecommerce_DWH")
DRIVER = os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")


def get_engine(database_name: str):
    connection_string = urllib.parse.quote_plus(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={database_name};"
        "Trusted_Connection=yes;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")


def main():
    dwh_engine = get_engine(DWH_DATABASE)

    with dwh_engine.begin() as connection:
        print("Starting OLTP -> DWH load...")

        # Clear the fact table before its dimensions.
        connection.execute(text("DELETE FROM dwh.FactSales"))
        connection.execute(text("DELETE FROM dwh.DimCustomer"))
        connection.execute(text("DELETE FROM dwh.DimProduct"))
        connection.execute(text("DELETE FROM dwh.DimStore"))
        connection.execute(text("DELETE FROM dwh.DimDate"))
        print("Existing DWH data deleted.")

        # Populate the date dimension for the data coverage period.
        connection.execute(text("""
            DECLARE @StartDate DATE = '2021-01-01';
            DECLARE @EndDate DATE = '2024-12-31';

            WHILE @StartDate <= @EndDate
            BEGIN
                INSERT INTO dwh.DimDate (
                    DateKey, FullDate, DayNumber, MonthNumber,
                    MonthName, QuarterNumber, YearNumber
                )
                VALUES (
                    CONVERT(INT, FORMAT(@StartDate, 'yyyyMMdd')),
                    @StartDate,
                    DAY(@StartDate),
                    MONTH(@StartDate),
                    DATENAME(MONTH, @StartDate),
                    DATEPART(QUARTER, @StartDate),
                    YEAR(@StartDate)
                );
                SET @StartDate = DATEADD(DAY, 1, @StartDate);
            END
        """))
        print("DimDate loaded.")

        # Load customer dimension.
        connection.execute(text(f"""
            INSERT INTO dwh.DimCustomer (
                CustomerID, FirstName, LastName, Email, City, SignupDate
            )
            SELECT CustomerID, FirstName, LastName, Email, City, SignupDate
            FROM [{OLTP_DATABASE}].oltp.Customers
        """))
        print("DimCustomer loaded.")

        # Load product dimension with the category name denormalized.
        connection.execute(text(f"""
            INSERT INTO dwh.DimProduct (
                ProductID, ProductName, CategoryName, Price
            )
            SELECT p.ProductID, p.ProductName, c.CategoryName, p.Price
            FROM [{OLTP_DATABASE}].oltp.Products AS p
            INNER JOIN [{OLTP_DATABASE}].oltp.Categories AS c
                ON p.CategoryID = c.CategoryID
        """))
        print("DimProduct loaded.")

        # Load store dimension.
        connection.execute(text(f"""
            INSERT INTO dwh.DimStore (StoreID, StoreName, City)
            SELECT StoreID, StoreName, City
            FROM [{OLTP_DATABASE}].oltp.Stores
        """))
        print("DimStore loaded.")

        # Load the fact table at order-item grain.
        connection.execute(text(f"""
            INSERT INTO dwh.FactSales (
                DateKey, CustomerKey, ProductKey, StoreKey,
                OrderID, OrderItemID, Quantity, UnitPrice, Discount, Revenue
            )
            SELECT
                dd.DateKey,
                dc.CustomerKey,
                dp.ProductKey,
                ds.StoreKey,
                o.OrderID,
                oi.OrderItemID,
                oi.Quantity,
                oi.UnitPrice,
                oi.Discount,
                CAST(oi.Quantity * oi.UnitPrice * (1 - oi.Discount) AS DECIMAL(18,2))
            FROM [{OLTP_DATABASE}].oltp.Orders AS o
            INNER JOIN [{OLTP_DATABASE}].oltp.OrderItems AS oi
                ON o.OrderID = oi.OrderID
            INNER JOIN dwh.DimDate AS dd
                ON o.OrderDate = dd.FullDate
            INNER JOIN dwh.DimCustomer AS dc
                ON o.CustomerID = dc.CustomerID
            INNER JOIN dwh.DimProduct AS dp
                ON oi.ProductID = dp.ProductID
            INNER JOIN dwh.DimStore AS ds
                ON o.StoreID = ds.StoreID
            WHERE o.Status = 'Completed'
        """))
        print("FactSales loaded.")
        print("OLTP -> DWH load completed successfully.")


if __name__ == "__main__":
    main()
