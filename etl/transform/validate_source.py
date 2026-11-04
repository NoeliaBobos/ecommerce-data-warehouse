from pathlib import Path
import sys

import pandas as pd

# -----------------------------
# PATH CONFIGURATION
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_RAW_PATH = PROJECT_ROOT / "data" / "source_raw"
LOG_PATH = PROJECT_ROOT / "logs" / "source_validation_log.txt"

# -----------------------------
# EXPECTED STRUCTURE
# -----------------------------

EXPECTED_HEADERS = {
    "customers.csv": ["customer_id", "first_name", "last_name", "email", "city", "signup_date"],
    "categories.csv": ["category_id", "category_name"],
    "products.csv": ["product_id", "product_name", "category_id", "price"],
    "stores.csv": ["store_id", "store_name", "city"],
    "orders.csv": ["order_id", "customer_id", "store_id", "order_date", "status"],
    "order_items.csv": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"],
}

VALID_STATUSES = {"Completed", "Pending", "Cancelled"}


# -----------------------------
# LOGGING
# -----------------------------

def log_message(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
    print(message)


def has_required_columns(df: pd.DataFrame, columns: list[str], file_name: str) -> bool:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        log_message(
            f"[ERROR] Cannot validate {file_name}; missing column(s): {', '.join(missing)}"
        )
        return False
    return True


# -----------------------------
# VALIDATION FUNCTIONS
# -----------------------------

def validate_headers(file_name: str, df: pd.DataFrame) -> bool:
    expected = EXPECTED_HEADERS[file_name]
    actual = list(df.columns)
    if actual != expected:
        log_message(
            f"[ERROR] Header mismatch in {file_name}. "
            f"Expected: {expected}; found: {actual}"
        )
        return False
    return True


def validate_primary_key(df: pd.DataFrame, column_name: str, file_name: str) -> bool:
    duplicates = df[column_name].duplicated(keep=False)
    if duplicates.any():
        count = int(duplicates.sum())
        log_message(
            f"[ERROR] Found {count} rows with duplicate values in {file_name}.{column_name}"
        )
        return False
    return True


def validate_not_null(df: pd.DataFrame, columns: list[str], file_name: str) -> bool:
    valid = True
    for column in columns:
        values = df[column]
        missing = values.isna()
        if pd.api.types.is_object_dtype(values.dtype) or pd.api.types.is_string_dtype(values.dtype):
            missing = missing | values.astype("string").str.strip().eq("")
        if missing.any():
            log_message(
                f"[ERROR] Found {int(missing.sum())} null/blank value(s) in {file_name}.{column}"
            )
            valid = False
    return valid


def validate_foreign_key(
    child_df: pd.DataFrame,
    child_col: str,
    parent_df: pd.DataFrame,
    parent_col: str,
    child_file: str,
) -> bool:
    invalid = ~child_df[child_col].isin(parent_df[parent_col])
    if invalid.any():
        log_message(
            f"[ERROR] Found {int(invalid.sum())} invalid foreign-key value(s) "
            f"in {child_file}.{child_col}"
        )
        return False
    return True


def validate_numeric_positive(df: pd.DataFrame, column: str, file_name: str) -> bool:
    numeric_values = pd.to_numeric(df[column], errors="coerce")
    invalid = numeric_values.isna() | numeric_values.le(0)
    if invalid.any():
        log_message(
            f"[ERROR] Found {int(invalid.sum())} non-numeric or non-positive value(s) "
            f"in {file_name}.{column}"
        )
        return False
    return True


def validate_discount(df: pd.DataFrame) -> bool:
    discounts = pd.to_numeric(df["discount"], errors="coerce")
    invalid = discounts.isna() | discounts.lt(0) | discounts.gt(1)
    if invalid.any():
        log_message(
            f"[ERROR] Found {int(invalid.sum())} invalid discount value(s) in order_items.csv; "
            "discount must be between 0 and 1"
        )
        return False
    return True


def validate_status(df: pd.DataFrame) -> bool:
    invalid = ~df["status"].isin(VALID_STATUSES)
    if invalid.any():
        log_message(
            f"[ERROR] Found {int(invalid.sum())} invalid status value(s) in orders.csv"
        )
        return False
    return True


def run_check(
    label: str,
    dataframes: dict[str, pd.DataFrame],
    requirements: dict[str, list[str]],
    validator,
    *args,
) -> bool:
    for file_name, columns in requirements.items():
        df = dataframes.get(file_name)
        if df is None:
            log_message(f"[ERROR] Skipping {label}: {file_name} could not be loaded")
            return False
        if not has_required_columns(df, columns, file_name):
            log_message(f"[ERROR] Skipping {label} because required columns are unavailable")
            return False

    result = validator(*args)
    if result:
        log_message(f"[OK] {label}")
    return result


# -----------------------------
# MAIN VALIDATION
# -----------------------------

def main() -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")

    log_message("SOURCE LAYER VALIDATION STARTED")
    log_message("--------------------------------")

    checks: list[bool] = []
    dataframes: dict[str, pd.DataFrame] = {}

    # Load all expected CSV files and check their headers.
    for file_name in EXPECTED_HEADERS:
        file_path = SOURCE_RAW_PATH / file_name
        if not file_path.is_file():
            log_message(f"[ERROR] Missing file: {file_name}")
            checks.append(False)
            continue

        try:
            df = pd.read_csv(file_path)
        except Exception as error:
            log_message(f"[ERROR] Could not read {file_name}: {error}")
            checks.append(False)
            continue

        dataframes[file_name] = df
        if df.empty:
            log_message(f"[ERROR] File contains no data rows: {file_name}")
            checks.append(False)
        checks.append(validate_headers(file_name, df))

    # Primary-key checks.
    primary_keys = {
        "customers.csv": "customer_id",
        "categories.csv": "category_id",
        "products.csv": "product_id",
        "stores.csv": "store_id",
        "orders.csv": "order_id",
        "order_items.csv": "order_item_id",
    }
    for file_name, column in primary_keys.items():
        checks.append(run_check(
            f"Primary key: {file_name}.{column}", dataframes,
            {file_name: [column]}, validate_primary_key,
            dataframes.get(file_name), column, file_name,
        ))

    # Required-value checks, including every primary key.
    not_null_rules = {
        "customers.csv": ["customer_id", "email"],
        "categories.csv": ["category_id", "category_name"],
        "products.csv": ["product_id", "price"],
        "stores.csv": ["store_id", "store_name", "city"],
        "orders.csv": ["order_id", "order_date", "status"],
        "order_items.csv": ["order_item_id", "quantity", "unit_price", "discount"],
    }
    for file_name, columns in not_null_rules.items():
        checks.append(run_check(
            f"Required values: {file_name}", dataframes,
            {file_name: columns}, validate_not_null,
            dataframes.get(file_name), columns, file_name,
        ))

    # Foreign-key checks.
    foreign_keys = [
        ("products.csv", "category_id", "categories.csv", "category_id"),
        ("orders.csv", "customer_id", "customers.csv", "customer_id"),
        ("orders.csv", "store_id", "stores.csv", "store_id"),
        ("order_items.csv", "order_id", "orders.csv", "order_id"),
        ("order_items.csv", "product_id", "products.csv", "product_id"),
    ]
    for child_file, child_col, parent_file, parent_col in foreign_keys:
        checks.append(run_check(
            f"Foreign key: {child_file}.{child_col} -> {parent_file}.{parent_col}",
            dataframes,
            {child_file: [child_col], parent_file: [parent_col]},
            validate_foreign_key,
            dataframes.get(child_file), child_col,
            dataframes.get(parent_file), parent_col, child_file,
        ))

    # Numeric and domain checks.
    numeric_rules = [
        ("products.csv", "price"),
        ("order_items.csv", "quantity"),
        ("order_items.csv", "unit_price"),
    ]
    for file_name, column in numeric_rules:
        checks.append(run_check(
            f"Positive numeric values: {file_name}.{column}", dataframes,
            {file_name: [column]}, validate_numeric_positive,
            dataframes.get(file_name), column, file_name,
        ))

    checks.append(run_check(
        "Discount values are between 0 and 1", dataframes,
        {"order_items.csv": ["discount"]}, validate_discount,
        dataframes.get("order_items.csv"),
    ))
    checks.append(run_check(
        "Order statuses are valid", dataframes,
        {"orders.csv": ["status"]}, validate_status,
        dataframes.get("orders.csv"),
    ))

    passed = sum(checks)
    failed = len(checks) - passed
    log_message("--------------------------------")
    if failed == 0:
        log_message(f"[PASS] SOURCE LAYER VALIDATION PASSED ({passed} checks)")
        return 0

    log_message(f"[FAIL] SOURCE LAYER VALIDATION FAILED ({failed} of {len(checks)} checks failed)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
