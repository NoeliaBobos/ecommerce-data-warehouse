# E-commerce Data Warehouse & Business Intelligence

A retail sales analytics project built with SQL Server, Python and Power BI. The project uses synthetic e-commerce data and a two-layer database design: a normalized OLTP database followed by a dimensional Data Warehouse (Star Schema).

## Tech stack

- Microsoft SQL Server
- Python: Pandas, SQLAlchemy and pyodbc
- ETL and source-data validation
- Star Schema dimensional modeling
- Power BI

## Repository structure

```text
.
├── dashboard/       # Power BI report (.pbix)
├── data/source_raw/ # Synthetic CSV source data
├── etl/
│   ├── extract/     # Source-data generation
│   ├── load/        # CSV -> OLTP -> DWH loads
│   └── transform/   # Source-data validation
├── logs/            # Runtime validation logs (not committed)
└── sql/             # OLTP, DWH, KPI and validation scripts
```

## Dataset

The included CSV files contain synthetic retail data: 5,000 customers, 500 products, 20,000 orders, 60,422 order items, 6 categories and 5 stores. Customer email addresses use the reserved `example.com` domain.

## Setup

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. In SQL Server Management Studio, run `sql/create_oltp.sql` and `sql/create_dwh.sql` to create the databases and tables.
3. Set the `SQL_SERVER` environment variable to your SQL Server host or instance. The default is `localhost`. The scripts use Windows Integrated Authentication by default. Optionally set `SQL_ODBC_DRIVER` if your installed ODBC driver has a different name.
4. Validate the included source files:

   ```bash
   python etl/transform/validate_source.py
   ```
5. Load the CSV files into OLTP, then load OLTP into the Data Warehouse:

   ```bash
   python etl/load/load_oltp_from_csv.py
   python etl/load/load_dwh_from_oltp.py
   ```
6. Open `dashboard/ecommerce_sales_dashboard.pbix` in Power BI Desktop and configure its SQL Server data source for your environment.

To regenerate the synthetic CSV files, run `python etl/extract/generate_source_data.py`. This overwrites the CSV files in `data/source_raw/`.

## Notes

- The included dataset is synthetic and does not contain real customer contact information.
- The SQL scripts create new databases; do not run them if databases with the same names already exist unless you have checked your environment first.
- The ETL scripts currently use Windows Integrated Authentication.
