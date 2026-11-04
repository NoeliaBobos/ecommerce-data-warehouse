import os
import pandas as pd

# -----------------------------
# PATH CONFIGURATION
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SOURCE_RAW_PATH = os.path.join(BASE_DIR, "data", "source_raw")
LOG_PATH = os.path.join(BASE_DIR, "logs", "source_validation_log.txt")

# -----------------------------
# EXPECTED STRUCTURE
# -----------------------------

EXPECTED_HEADERS = {
    "customers.csv": ["customer_id", "first_name", "last_name", "email", "city", "signup_date"],
    "categories.csv": ["category_id", "category_name"],
    "products.csv": ["product_id", "product_name", "category_id", "price"],
    "stores.csv": ["store_id", "store_name", "city"],
    "orders.csv": ["order_id", "customer_id", "store_id", "order_date", "status"],
    "order_items.csv": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"]
}

VALID_STATUSES = ["Completed", "Pending", "Cancelled"]

# -----------------------------
# LOG FUNCTION
# -----------------------------

def log_message(message):
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
    print(message)

# -----------------------------
# VALIDATION FUNCTIONS
# -----------------------------

def validate_headers(file_name, df):
    expected = EXPECTED_HEADERS[file_name]
    if list(df.columns) != expected:
        log_message(f"[ERROR] Header mismatch in {file_name}")
        return False
    return True

def validate_primary_key(df, column_name, file_name):
    if df[column_name].duplicated().any():
        log_message(f"[ERROR] Duplicate values found in {file_name}.{column_name}")
        return False
    return True

def validate_not_null(df, columns, file_name):
    for col in columns:
        if df[col].isnull().any():
            log_message(f"[ERROR] Null values found in {file_name}.{col}")
            return False
    return True

def validate_foreign_key(child_df, child_col, parent_df, parent_col, child_file):
    if not child_df[child_col].isin(parent_df[parent_col]).all():
        log_message(f"[ERROR] Invalid foreign key in {child_file}.{child_col}")
        return False
    return True

def validate_numeric_positive(df, column, file_name):
    if (df[column] <= 0).any():
        log_message(f"[ERROR] Non-positive values in {file_name}.{column}")
        return False
    return True

def validate_discount(df):
    if ((df["discount"] < 0) | (df["discount"] > 1)).any():
        log_message("[ERROR] Invalid discount values in order_items.csv")
        return False
    return True

def validate_status(df):
    if not df["status"].isin(VALID_STATUSES).all():
        log_message("[ERROR] Invalid status values in orders.csv")
        return False
    return True

# -----------------------------
# MAIN VALIDATION
# -----------------------------

def main():

    # Clear previous log
    open(LOG_PATH, "w").close()

    log_message("SOURCE LAYER VALIDATION STARTED")
    log_message("--------------------------------")

    # Load files
    dfs = {}
    for file_name in EXPECTED_HEADERS.keys():
        file_path = os.path.join(SOURCE_RAW_PATH, file_name)
        if not os.path.exists(file_path):
            log_message(f"[ERROR] Missing file: {file_name}")
            return
        dfs[file_name] = pd.read_csv(file_path)

    # Header validation
    for file_name, df in dfs.items():
        validate_headers(file_name, df)

    # Primary key validation
    validate_primary_key(dfs["customers.csv"], "customer_id", "customers.csv")
    validate_primary_key(dfs["categories.csv"], "category_id", "categories.csv")
    validate_primary_key(dfs["products.csv"], "product_id", "products.csv")
    validate_primary_key(dfs["stores.csv"], "store_id", "stores.csv")
    validate_primary_key(dfs["orders.csv"], "order_id", "orders.csv")
    validate_primary_key(dfs["order_items.csv"], "order_item_id", "order_items.csv")

    # Not null checks
    validate_not_null(dfs["customers.csv"], ["customer_id", "email"], "customers.csv")
    validate_not_null(dfs["products.csv"], ["product_id", "price"], "products.csv")
    validate_not_null(dfs["orders.csv"], ["order_id", "order_date"], "orders.csv")
    validate_not_null(dfs["order_items.csv"], ["order_item_id", "quantity"], "order_items.csv")

    # Foreign key validation
    validate_foreign_key(dfs["products.csv"], "category_id", dfs["categories.csv"], "category_id", "products.csv")
    validate_foreign_key(dfs["orders.csv"], "customer_id", dfs["customers.csv"], "customer_id", "orders.csv")
    validate_foreign_key(dfs["orders.csv"], "store_id", dfs["stores.csv"], "store_id", "orders.csv")
    validate_foreign_key(dfs["order_items.csv"], "order_id", dfs["orders.csv"], "order_id", "order_items.csv")
    validate_foreign_key(dfs["order_items.csv"], "product_id", dfs["products.csv"], "product_id", "order_items.csv")

    # Numeric validation
    validate_numeric_positive(dfs["products.csv"], "price", "products.csv")
    validate_numeric_positive(dfs["order_items.csv"], "quantity", "order_items.csv")
    validate_numeric_positive(dfs["order_items.csv"], "unit_price", "order_items.csv")

    validate_discount(dfs["order_items.csv"])
    validate_status(dfs["orders.csv"])

    log_message("--------------------------------")
    log_message("SOURCE LAYER VALIDATION COMPLETED")

if __name__ == "__main__":
    main()