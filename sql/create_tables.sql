-- Stage 2 SQLite schema for the Retail Revenue Intelligence Platform.
-- Tables are created before pandas inserts data with if_exists="append".

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity REAL,
    invoice_date TEXT,
    unit_price REAL,
    customer_id TEXT,
    country TEXT,
    invoice_date_only TEXT,
    invoice_year INTEGER,
    invoice_month INTEGER,
    invoice_month_name TEXT,
    invoice_day_name TEXT,
    invoice_hour INTEGER,
    invoice_year_month TEXT,
    revenue REAL,
    is_cancelled INTEGER,
    has_customer_id INTEGER,
    is_invalid_transaction INTEGER
);

CREATE TABLE IF NOT EXISTS sales_transactions (
    sales_transaction_id INTEGER PRIMARY KEY,
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity REAL,
    invoice_date TEXT,
    unit_price REAL,
    customer_id TEXT,
    country TEXT,
    invoice_date_only TEXT,
    invoice_year INTEGER,
    invoice_month INTEGER,
    invoice_month_name TEXT,
    invoice_day_name TEXT,
    invoice_hour INTEGER,
    invoice_year_month TEXT,
    revenue REAL,
    is_cancelled INTEGER,
    has_customer_id INTEGER,
    is_invalid_transaction INTEGER
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    first_purchase_date TEXT,
    last_purchase_date TEXT,
    total_orders INTEGER,
    total_quantity REAL,
    total_revenue REAL,
    average_order_value REAL,
    country_count INTEGER,
    main_country TEXT
);

CREATE TABLE IF NOT EXISTS products (
    stock_code TEXT PRIMARY KEY,
    description TEXT,
    total_quantity_sold REAL,
    total_revenue REAL,
    number_of_orders INTEGER,
    number_of_customers INTEGER,
    average_unit_price REAL
);

CREATE TABLE IF NOT EXISTS countries (
    country TEXT PRIMARY KEY,
    total_revenue REAL,
    total_orders INTEGER,
    total_customers INTEGER,
    total_quantity_sold REAL,
    average_order_value REAL
);

CREATE TABLE IF NOT EXISTS monthly_sales (
    invoice_year_month TEXT PRIMARY KEY,
    total_revenue REAL,
    total_orders INTEGER,
    total_quantity_sold REAL,
    total_customers INTEGER,
    average_order_value REAL
);

CREATE INDEX IF NOT EXISTS idx_transactions_invoice_no ON transactions (invoice_no);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions (customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_stock_code ON transactions (stock_code);
CREATE INDEX IF NOT EXISTS idx_transactions_country ON transactions (country);
CREATE INDEX IF NOT EXISTS idx_transactions_year_month ON transactions (invoice_year_month);

CREATE INDEX IF NOT EXISTS idx_sales_invoice_no ON sales_transactions (invoice_no);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales_transactions (customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_stock_code ON sales_transactions (stock_code);
CREATE INDEX IF NOT EXISTS idx_sales_country ON sales_transactions (country);
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales_transactions (invoice_year_month);
