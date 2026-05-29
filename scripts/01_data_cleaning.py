"""
Stage 1 data cleaning for the Retail Revenue Intelligence Platform.

Run this script from the project root:
    python scripts/01_data_cleaning.py
"""

from pathlib import Path
import re

import pandas as pd


# Project folders are built from the script location, so no local computer path is hard-coded.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def find_raw_file(raw_dir: Path) -> Path:
    """Find one supported raw data file in the raw data folder."""
    raw_files = sorted(
        path
        for path in raw_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not raw_files:
        raise FileNotFoundError(
            f"No supported raw file found in {raw_dir}. "
            "Add a .xlsx, .xls, or .csv file to continue."
        )

    if len(raw_files) > 1:
        file_names = ", ".join(path.name for path in raw_files)
        raise ValueError(
            "More than one supported raw file was found. "
            f"Please keep only one raw dataset in {raw_dir}: {file_names}"
        )

    return raw_files[0]


def load_raw_data(raw_file: Path) -> pd.DataFrame:
    """Load CSV or Excel data. Excel workbooks may contain one or more sheets."""
    if raw_file.suffix.lower() in {".xlsx", ".xls"}:
        sheets = pd.read_excel(raw_file, sheet_name=None, dtype=object)
        print(f"Excel sheets detected: {list(sheets.keys())}")
        return pd.concat(sheets.values(), ignore_index=True)

    try:
        return pd.read_csv(raw_file, dtype=object)
    except UnicodeDecodeError:
        return pd.read_csv(raw_file, dtype=object, encoding="latin1")


def standardize_column_name(column_name: str) -> str:
    """Convert expected retail column names into clean snake_case names."""
    column_text = str(column_name).strip()
    lookup_key = re.sub(r"[^a-z0-9]", "", column_text.lower())

    column_mapping = {
        "invoice": "invoice_no",
        "invoiceno": "invoice_no",
        "stockcode": "stock_code",
        "description": "description",
        "quantity": "quantity",
        "invoicedate": "invoice_date",
        "price": "unit_price",
        "unitprice": "unit_price",
        "customerid": "customer_id",
        "country": "country",
    }

    if lookup_key in column_mapping:
        return column_mapping[lookup_key]

    snake_case_name = re.sub(r"[^a-z0-9]+", "_", column_text.lower()).strip("_")
    return snake_case_name


def clean_identifier_value(value):
    """Clean identifier values without turning missing values into text."""
    if pd.isna(value):
        return pd.NA

    text_value = str(value).strip()
    if text_value == "" or text_value.lower() in {"nan", "none", "nat"}:
        return pd.NA

    if re.fullmatch(r"-?\d+\.0", text_value):
        text_value = text_value[:-2]

    return text_value


def clean_identifier_series(series: pd.Series) -> pd.Series:
    """Clean a full identifier column and keep missing values as missing."""
    return series.map(clean_identifier_value).astype("string")


def clean_text_series(series: pd.Series) -> pd.Series:
    """Trim text fields and keep blanks as missing values."""
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.replace("", pd.NA)
    return cleaned


def main() -> None:
    print("Starting Stage 1 data cleaning...")

    # Make sure required folders exist before saving outputs.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "dashboard" / "dashboard_screenshots").mkdir(parents=True, exist_ok=True)
    for folder_name in ["database", "notebooks", "scripts", "sql", "reports", "visuals"]:
        (PROJECT_ROOT / folder_name).mkdir(parents=True, exist_ok=True)
    print("Project folder structure checked.")

    raw_file = find_raw_file(RAW_DIR)
    print(f"Detected raw file: {raw_file.relative_to(PROJECT_ROOT)}")

    raw_df = load_raw_data(raw_file)
    raw_row_count, raw_column_count = raw_df.shape
    print(f"Raw dataset shape: {raw_df.shape}")
    print("Raw column names:")
    print(list(raw_df.columns))
    print("Raw data types:")
    print(raw_df.dtypes)

    df = raw_df.copy()
    df.columns = [standardize_column_name(column) for column in df.columns]
    print("Standardized column names:")
    print(list(df.columns))

    duplicate_column_names = df.columns[df.columns.duplicated()].tolist()
    if duplicate_column_names:
        raise ValueError(f"Duplicate column names after standardization: {duplicate_column_names}")

    required_columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]
    missing_required_columns = [column for column in required_columns if column not in df.columns]
    if missing_required_columns:
        raise ValueError(f"Missing required columns after standardization: {missing_required_columns}")

    rows_before_duplicates = len(df)
    df = df.drop_duplicates().copy()
    duplicate_rows_removed = rows_before_duplicates - len(df)
    print(f"Duplicate rows removed: {duplicate_rows_removed}")

    # Clean identifier and text columns before creating flags.
    df["invoice_no"] = clean_identifier_series(df["invoice_no"])
    df["stock_code"] = clean_identifier_series(df["stock_code"])
    df["customer_id"] = clean_identifier_series(df["customer_id"])
    df["description"] = clean_text_series(df["description"])
    df["country"] = clean_text_series(df["country"])
    print("Identifier and text columns cleaned.")

    # Convert analytical fields to the right types.
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    print("Date and numeric columns parsed.")

    # Create date features for later SQL, BI, and forecasting work.
    df["invoice_date_only"] = df["invoice_date"].dt.date
    df["invoice_year"] = df["invoice_date"].dt.year.astype("Int64")
    df["invoice_month"] = df["invoice_date"].dt.month.astype("Int64")
    df["invoice_month_name"] = df["invoice_date"].dt.month_name()
    df["invoice_day_name"] = df["invoice_date"].dt.day_name()
    df["invoice_hour"] = df["invoice_date"].dt.hour.astype("Int64")
    df["invoice_year_month"] = df["invoice_date"].dt.to_period("M").astype("string")
    print("Date features created.")

    # Revenue remains negative for cancelled or returned rows in the main cleaned dataset.
    df["revenue"] = df["quantity"] * df["unit_price"]
    print("Revenue column created.")

    invoice_starts_with_c = (
        df["invoice_no"].notna()
        & df["invoice_no"].str.upper().str.startswith("C", na=False)
    )
    negative_quantity = df["quantity"].lt(0).fillna(False)
    df["is_cancelled"] = invoice_starts_with_c | negative_quantity
    print("Cancellation flag created.")

    df["has_customer_id"] = df["customer_id"].notna()
    print("Customer ID availability flag created.")

    missing_required_business_fields = (
        df["invoice_no"].isna()
        | df["stock_code"].isna()
        | df["description"].isna()
        | df["invoice_date"].isna()
        | df["country"].isna()
    )
    missing_quantity_count = int(df["quantity"].isna().sum())
    missing_unit_price_count = int(df["unit_price"].isna().sum())
    invalid_quantity = df["quantity"].isna() | df["quantity"].eq(0)
    invalid_unit_price = df["unit_price"].isna() | df["unit_price"].le(0)
    df["is_invalid_transaction"] = (
        missing_required_business_fields | invalid_unit_price | invalid_quantity
    )
    print("Invalid transaction flag created.")

    sales_df = df[
        (~df["is_cancelled"])
        & (~df["is_invalid_transaction"])
        & (df["quantity"] > 0)
        & (df["unit_price"] > 0)
    ].copy()
    print("Sales-only dataset created.")

    valid_invoice_dates = df["invoice_date"].dropna()
    if valid_invoice_dates.empty:
        invoice_date_range = ""
    else:
        invoice_date_range = (
            f"{valid_invoice_dates.min()} to {valid_invoice_dates.max()}"
        )

    summary_data = [
        ("raw row count", raw_row_count),
        ("raw column count", raw_column_count),
        ("duplicate rows removed", duplicate_rows_removed),
        ("rows with missing customer_id", int(df["customer_id"].isna().sum())),
        ("cancelled transaction count", int(df["is_cancelled"].sum())),
        ("negative quantity count", int(negative_quantity.sum())),
        ("missing quantity count", missing_quantity_count),
        ("missing unit_price count", missing_unit_price_count),
        ("invalid quantity count", int(invalid_quantity.sum())),
        ("invalid unit_price count", int(invalid_unit_price.sum())),
        ("final cleaned transaction rows", len(df)),
        ("final sales-only rows", len(sales_df)),
        ("total revenue in sales-only dataset", round(float(sales_df["revenue"].sum()), 2)),
        ("number of countries", int(df["country"].dropna().nunique())),
        ("number of unique customers", int(df.loc[df["customer_id"].notna(), "customer_id"].nunique())),
        ("number of unique products", int(df["stock_code"].dropna().nunique())),
        ("invoice date range", invoice_date_range),
    ]
    summary_df = pd.DataFrame(summary_data, columns=["metric", "value"])
    print("Cleaning summary table created.")

    clean_output_path = PROCESSED_DIR / "clean_retail_transactions.csv"
    sales_output_path = PROCESSED_DIR / "sales_transactions_only.csv"
    summary_output_path = PROCESSED_DIR / "data_cleaning_summary.csv"

    df.to_csv(clean_output_path, index=False, na_rep="")
    sales_df.to_csv(sales_output_path, index=False, na_rep="")
    summary_df.to_csv(summary_output_path, index=False)
    print("Processed files saved:")
    print(f"- {clean_output_path.relative_to(PROJECT_ROOT)}")
    print(f"- {sales_output_path.relative_to(PROJECT_ROOT)}")
    print(f"- {summary_output_path.relative_to(PROJECT_ROOT)}")

    print("\nFinal validation")
    print(f"Clean retail transactions shape: {df.shape}")
    print(f"Sales-only transactions shape: {sales_df.shape}")
    print(f"Total sales-only revenue: {sales_df['revenue'].sum():,.2f}")
    print(f"Cancellation count: {int(df['is_cancelled'].sum()):,}")
    print(f"Missing customer_id count: {int(df['customer_id'].isna().sum()):,}")
    print("Stage 1 data cleaning completed.")


if __name__ == "__main__":
    main()
