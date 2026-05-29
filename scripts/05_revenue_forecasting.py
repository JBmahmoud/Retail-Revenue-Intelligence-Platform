"""
Stage 4: Revenue forecasting using weekly sales revenue.

Run from the project root:
    python scripts/05_revenue_forecasting.py
"""

from importlib.util import find_spec
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "retail_analytics.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "forecasting"

WEEKLY_REVENUE_PATH = OUTPUT_DIR / "weekly_revenue.csv"
MONTHLY_REVENUE_PATH = OUTPUT_DIR / "monthly_revenue_for_forecasting.csv"
MODEL_COMPARISON_PATH = OUTPUT_DIR / "forecast_model_comparison.csv"
ACTUAL_VS_FORECAST_PATH = OUTPUT_DIR / "weekly_actual_vs_forecast.csv"
FUTURE_WEEKLY_PATH = OUTPUT_DIR / "future_weekly_forecast.csv"
FUTURE_MONTHLY_PATH = OUTPUT_DIR / "future_monthly_forecast.csv"
BUSINESS_SUMMARY_PATH = OUTPUT_DIR / "forecast_business_summary.csv"
RECOMMENDATIONS_PATH = OUTPUT_DIR / "forecast_recommendations.csv"


def require_database() -> None:
    """Stop with a clear error if the Stage 2 database is missing."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Required database is missing. Run "
            "python scripts/02_build_sql_database.py first."
        )


def validate_sales_transactions_table(connection: sqlite3.Connection) -> None:
    """Check that the source table needed for forecasting exists."""
    table_exists = connection.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'sales_transactions'
        """
    ).fetchone()[0]

    if table_exists == 0:
        raise ValueError("Required table is missing from the database: sales_transactions")


def load_sales_transactions(connection: sqlite3.Connection) -> pd.DataFrame:
    """Load valid positive sales transactions for forecasting."""
    query = """
    SELECT
        invoice_no,
        invoice_date,
        quantity,
        unit_price,
        revenue,
        is_cancelled,
        is_invalid_transaction
    FROM sales_transactions
    WHERE invoice_date IS NOT NULL
      AND revenue IS NOT NULL
      AND quantity > 0
      AND unit_price > 0
      AND revenue > 0
      AND is_cancelled = 0
      AND is_invalid_transaction = 0
    """
    sales = pd.read_sql_query(query, connection)

    if sales.empty:
        raise ValueError("No valid positive sales records found for forecasting.")

    sales["invoice_no"] = sales["invoice_no"].astype("string")
    sales["invoice_date"] = pd.to_datetime(sales["invoice_date"], errors="coerce")
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales["revenue"] = pd.to_numeric(sales["revenue"], errors="coerce")
    sales = sales.dropna(subset=["invoice_no", "invoice_date", "quantity", "revenue"])

    if sales.empty:
        raise ValueError("Sales records became empty after type validation.")

    return sales


def aggregate_weekly_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue into existing Monday-start weekly periods."""
    weekly_sales = sales.copy()
    weekly_sales["week_start_date"] = weekly_sales["invoice_date"].dt.to_period(
        "W-SUN"
    ).apply(lambda period: period.start_time)

    weekly = (
        weekly_sales.groupby("week_start_date", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("invoice_no", "nunique"),
            total_quantity=("quantity", "sum"),
        )
        .sort_values("week_start_date")
    )
    weekly["average_order_value"] = weekly["total_revenue"] / weekly["total_orders"]
    return weekly


def aggregate_monthly_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by month for executive trend reporting."""
    monthly_sales = sales.copy()
    monthly_sales["month_start_date"] = monthly_sales["invoice_date"].dt.to_period(
        "M"
    ).dt.to_timestamp()
    monthly_sales["invoice_year_month"] = monthly_sales["month_start_date"].dt.strftime("%Y-%m")

    monthly = (
        monthly_sales.groupby(["invoice_year_month", "month_start_date"], as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("invoice_no", "nunique"),
            total_quantity=("quantity", "sum"),
        )
        .sort_values("month_start_date")
    )
    monthly["average_order_value"] = monthly["total_revenue"] / monthly["total_orders"]
    return monthly


def split_train_test(weekly: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Use the last 8 weeks as test when enough weekly periods exist."""
    if len(weekly) > 8:
        test_weeks = 8
    else:
        test_weeks = max(1, int(round(len(weekly) * 0.2)))

    train = weekly.iloc[:-test_weeks].copy()
    test = weekly.iloc[-test_weeks:].copy()

    if train.empty:
        raise ValueError("Not enough weekly periods to create a train/test split.")

    return train, test


def safe_mape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Calculate MAPE while avoiding division by zero."""
    actual = np.asarray(actual, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    non_zero_mask = actual != 0

    if not non_zero_mask.any():
        return np.nan

    return float(np.mean(np.abs((actual[non_zero_mask] - forecast[non_zero_mask]) / actual[non_zero_mask])) * 100)


def evaluate_forecast(actual: np.ndarray, forecast: np.ndarray) -> tuple[float, float, float]:
    """Return MAE, RMSE, and safe MAPE."""
    actual = np.asarray(actual, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    mae = float(np.mean(np.abs(actual - forecast)))
    rmse = float(np.sqrt(np.mean((actual - forecast) ** 2)))
    mape = safe_mape(actual, forecast)
    return round(mae, 2), round(rmse, 2), round(mape, 2) if not np.isnan(mape) else np.nan


def evaluate_naive(weekly: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Predict each test week using the previous observed weekly revenue."""
    all_revenue = weekly["total_revenue"].to_numpy(dtype=float)
    test_start = len(train)
    forecast = [all_revenue[index - 1] for index in range(test_start, len(weekly))]
    return np.maximum(np.asarray(forecast, dtype=float), 0)


def evaluate_moving_average(weekly: pd.DataFrame, train: pd.DataFrame, window: int = 4) -> np.ndarray:
    """Predict each test week using the previous observed 4-week average."""
    all_revenue = weekly["total_revenue"].to_numpy(dtype=float)
    forecast = []

    for index in range(len(train), len(weekly)):
        start_index = max(0, index - window)
        forecast.append(all_revenue[start_index:index].mean())

    return np.maximum(np.asarray(forecast, dtype=float), 0)


def evaluate_linear_trend(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Fit a simple linear trend on the training weeks and predict the test weeks."""
    train_x = np.arange(len(train), dtype=float)
    train_y = train["total_revenue"].to_numpy(dtype=float)
    test_x = np.arange(len(train), len(train) + len(test), dtype=float)

    slope, intercept = np.polyfit(train_x, train_y, deg=1)
    forecast = slope * test_x + intercept
    return np.maximum(forecast, 0)


def evaluate_exponential_smoothing(train: pd.DataFrame, test_periods: int) -> tuple[np.ndarray | None, str]:
    """Use statsmodels exponential smoothing only when available."""
    if find_spec("statsmodels") is None:
        return None, "Skipped because statsmodels is not installed."

    try:
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing

        model = SimpleExpSmoothing(
            train["total_revenue"].to_numpy(dtype=float),
            initialization_method="estimated",
        )
        fitted_model = model.fit(optimized=True)
        forecast = fitted_model.forecast(test_periods)
        return np.maximum(np.asarray(forecast, dtype=float), 0), "Simple exponential smoothing."
    except Exception as exc:  # pragma: no cover - defensive for optional dependency
        return None, f"Skipped because statsmodels failed: {exc}"


def forecast_future_revenue(
    model_name: str,
    weekly: pd.DataFrame,
    periods: int,
    moving_average_window: int = 4,
) -> np.ndarray:
    """Generate non-negative future weekly forecasts using the selected model."""
    history = list(weekly["total_revenue"].to_numpy(dtype=float))

    if model_name == "Naive Forecast":
        forecast = np.repeat(history[-1], periods)

    elif model_name == "4-Week Moving Average":
        forecast_values = []
        rolling_history = history.copy()
        for _ in range(periods):
            next_value = float(np.mean(rolling_history[-moving_average_window:]))
            forecast_values.append(next_value)
            rolling_history.append(next_value)
        forecast = np.asarray(forecast_values, dtype=float)

    elif model_name == "Linear Trend Regression":
        x = np.arange(len(history), dtype=float)
        y = np.asarray(history, dtype=float)
        future_x = np.arange(len(history), len(history) + periods, dtype=float)
        slope, intercept = np.polyfit(x, y, deg=1)
        forecast = slope * future_x + intercept

    elif model_name == "Exponential Smoothing":
        if find_spec("statsmodels") is None:
            raise RuntimeError("Exponential Smoothing selected but statsmodels is unavailable.")
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing

        model = SimpleExpSmoothing(np.asarray(history, dtype=float), initialization_method="estimated")
        fitted_model = model.fit(optimized=True)
        forecast = np.asarray(fitted_model.forecast(periods), dtype=float)

    else:
        raise ValueError(f"Unsupported model for future forecasting: {model_name}")

    return np.maximum(forecast, 0)


def build_model_outputs(
    weekly: pd.DataFrame,
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Evaluate all simple models and return comparison and actual-vs-forecast outputs."""
    actual = test["total_revenue"].to_numpy(dtype=float)
    actual_vs_forecast = pd.DataFrame(
        {
            "week_start_date": test["week_start_date"],
            "actual_revenue": actual,
        }
    )

    model_rows = []

    naive_forecast = evaluate_naive(weekly, train, test)
    actual_vs_forecast["naive_forecast"] = naive_forecast
    mae, rmse, mape = evaluate_forecast(actual, naive_forecast)
    model_rows.append(
        {
            "model_name": "Naive Forecast",
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "notes": "Uses the previous observed weekly revenue as the next forecast.",
        }
    )

    moving_average_forecast = evaluate_moving_average(weekly, train, window=4)
    actual_vs_forecast["moving_average_forecast"] = moving_average_forecast
    mae, rmse, mape = evaluate_forecast(actual, moving_average_forecast)
    model_rows.append(
        {
            "model_name": "4-Week Moving Average",
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "notes": "Uses the average of the previous 4 observed weeks.",
        }
    )

    linear_trend_forecast = evaluate_linear_trend(train, test)
    actual_vs_forecast["linear_trend_forecast"] = linear_trend_forecast
    mae, rmse, mape = evaluate_forecast(actual, linear_trend_forecast)
    model_rows.append(
        {
            "model_name": "Linear Trend Regression",
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "notes": "Uses a time index as the only regression feature.",
        }
    )

    exponential_forecast, exponential_note = evaluate_exponential_smoothing(train, len(test))
    if exponential_forecast is not None:
        actual_vs_forecast["exponential_smoothing_forecast"] = exponential_forecast
        mae, rmse, mape = evaluate_forecast(actual, exponential_forecast)
        model_rows.append(
            {
                "model_name": "Exponential Smoothing",
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "notes": exponential_note,
            }
        )
    else:
        print(f"Exponential Smoothing skipped: {exponential_note}")
        model_rows.append(
            {
                "model_name": "Exponential Smoothing",
                "mae": np.nan,
                "rmse": np.nan,
                "mape": np.nan,
                "notes": exponential_note,
            }
        )

    comparison = pd.DataFrame(model_rows)
    evaluated_models = comparison.dropna(subset=["mae"]).copy()
    best_model = evaluated_models.sort_values(["mae", "rmse", "mape"]).iloc[0]["model_name"]

    forecast_columns = [column for column in actual_vs_forecast.columns if column.endswith("_forecast")]
    actual_vs_forecast[forecast_columns] = actual_vs_forecast[forecast_columns].round(2)
    actual_vs_forecast["actual_revenue"] = actual_vs_forecast["actual_revenue"].round(2)

    return comparison, actual_vs_forecast, best_model


def future_week_starts(last_week_start: pd.Timestamp, periods: int) -> pd.DatetimeIndex:
    """Create future Monday week start dates."""
    return pd.date_range(start=last_week_start + pd.Timedelta(days=7), periods=periods, freq="W-MON")


def months_after_last_history(monthly: pd.DataFrame) -> pd.DatetimeIndex:
    """Return the next 3 full calendar months after the historical monthly data."""
    last_month_start = monthly["month_start_date"].max()
    first_future_month = last_month_start + pd.offsets.MonthBegin(1)
    return pd.date_range(start=first_future_month, periods=3, freq="MS")


def extended_future_period_count(last_week_start: pd.Timestamp, future_months: pd.DatetimeIndex) -> int:
    """Calculate how many future weekly forecasts are needed to cover the future months."""
    last_future_month_end = future_months[-1] + pd.offsets.MonthEnd(0)
    future_dates = pd.date_range(
        start=last_week_start + pd.Timedelta(days=7),
        end=last_future_month_end,
        freq="W-MON",
    )
    return len(future_dates)


def build_future_forecasts(
    weekly: pd.DataFrame,
    monthly: pd.DataFrame,
    best_model: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create next 8 weekly forecasts and exactly 3 future monthly forecasts."""
    last_week_start = weekly["week_start_date"].max()
    future_months = months_after_last_history(monthly)
    extended_periods = extended_future_period_count(last_week_start, future_months)

    extended_week_dates = future_week_starts(last_week_start, extended_periods)
    extended_forecast = forecast_future_revenue(best_model, weekly, extended_periods)
    extended_weekly = pd.DataFrame(
        {
            "week_start_date": extended_week_dates,
            "forecast_revenue": extended_forecast,
            "model_used": best_model,
        }
    )

    future_weekly = extended_weekly.head(8).copy()

    extended_weekly["month_start_date"] = extended_weekly["week_start_date"].dt.to_period(
        "M"
    ).dt.to_timestamp()
    future_monthly = (
        extended_weekly[extended_weekly["month_start_date"].isin(future_months)]
        .groupby("month_start_date", as_index=False)
        .agg(forecast_revenue=("forecast_revenue", "sum"))
    )
    future_monthly = (
        pd.DataFrame({"month_start_date": future_months})
        .merge(future_monthly, on="month_start_date", how="left")
        .fillna({"forecast_revenue": 0})
    )
    future_monthly["forecast_month"] = future_monthly["month_start_date"].dt.strftime("%Y-%m")
    future_monthly["model_used"] = best_model
    future_monthly = future_monthly[["forecast_month", "forecast_revenue", "model_used"]]

    future_weekly["forecast_revenue"] = future_weekly["forecast_revenue"].round(2)
    future_monthly["forecast_revenue"] = future_monthly["forecast_revenue"].round(2)

    return future_weekly, future_monthly


def classify_forecast_direction(weekly: pd.DataFrame, future_weekly: pd.DataFrame) -> str:
    """Classify forecast direction using a 5 percent threshold."""
    latest_actual_average = weekly.tail(8)["total_revenue"].mean()
    forecast_average = future_weekly["forecast_revenue"].mean()

    if forecast_average > latest_actual_average * 1.05:
        return "Increasing"
    if forecast_average < latest_actual_average * 0.95:
        return "Decreasing"
    return "Stable"


def build_business_summary(
    weekly: pd.DataFrame,
    future_weekly: pd.DataFrame,
    future_monthly: pd.DataFrame,
    model_comparison: pd.DataFrame,
    best_model: str,
    forecast_direction: str,
) -> pd.DataFrame:
    """Build a two-column dashboard-ready forecast summary."""
    best_row = model_comparison[model_comparison["model_name"] == best_model].iloc[0]
    highest_forecast_week = future_weekly.sort_values("forecast_revenue", ascending=False).iloc[0]
    lowest_forecast_week = future_weekly.sort_values("forecast_revenue", ascending=True).iloc[0]

    summary_rows = [
        ("best_model", best_model),
        ("best_model_mae", round(float(best_row["mae"]), 2)),
        ("best_model_rmse", round(float(best_row["rmse"]), 2)),
        ("best_model_mape", round(float(best_row["mape"]), 2)),
        ("historical_weekly_average_revenue", round(float(weekly["total_revenue"].mean()), 2)),
        ("latest_week_revenue", round(float(weekly.iloc[-1]["total_revenue"]), 2)),
        ("forecast_next_8_weeks_total", round(float(future_weekly["forecast_revenue"].sum()), 2)),
        ("forecast_next_3_months_total", round(float(future_monthly["forecast_revenue"].sum()), 2)),
        ("highest_forecast_week", highest_forecast_week["week_start_date"].strftime("%Y-%m-%d")),
        ("lowest_forecast_week", lowest_forecast_week["week_start_date"].strftime("%Y-%m-%d")),
        ("forecast_direction", forecast_direction),
    ]
    return pd.DataFrame(summary_rows, columns=["metric", "value"])


def build_recommendations(forecast_direction: str) -> pd.DataFrame:
    """Create simple business recommendations from the forecast signal."""
    recommendations = {
        "Increasing": (
            "Forecast is more than 5% above the latest 8-week historical average.",
            "Prepare stock, staffing, and marketing capacity for higher demand.",
        ),
        "Decreasing": (
            "Forecast is more than 5% below the latest 8-week historical average.",
            "Investigate customer retention, product demand, and promotional opportunities.",
        ),
        "Stable": (
            "Forecast is within 5% of the latest 8-week historical average.",
            "Focus on margin improvement, high-value customer retention, and inventory discipline.",
        ),
    }
    interpretation, action = recommendations[forecast_direction]
    return pd.DataFrame(
        [(forecast_direction, interpretation, action)],
        columns=["forecast_signal", "business_interpretation", "recommended_action"],
    )


def save_csv_outputs(
    weekly: pd.DataFrame,
    monthly: pd.DataFrame,
    model_comparison: pd.DataFrame,
    actual_vs_forecast: pd.DataFrame,
    future_weekly: pd.DataFrame,
    future_monthly: pd.DataFrame,
    business_summary: pd.DataFrame,
    recommendations: pd.DataFrame,
) -> list[Path]:
    """Save all Stage 4 forecasting CSV outputs."""
    weekly_output = weekly.copy()
    weekly_output["week_start_date"] = weekly_output["week_start_date"].dt.strftime("%Y-%m-%d")
    weekly_output = weekly_output.round(
        {
            "total_revenue": 2,
            "total_quantity": 2,
            "average_order_value": 2,
        }
    )

    monthly_output = monthly.copy()
    monthly_output["month_start_date"] = monthly_output["month_start_date"].dt.strftime("%Y-%m-%d")
    monthly_output = monthly_output.round(
        {
            "total_revenue": 2,
            "total_quantity": 2,
            "average_order_value": 2,
        }
    )

    actual_output = actual_vs_forecast.copy()
    actual_output["week_start_date"] = actual_output["week_start_date"].dt.strftime("%Y-%m-%d")

    future_weekly_output = future_weekly.copy()
    future_weekly_output["week_start_date"] = future_weekly_output["week_start_date"].dt.strftime("%Y-%m-%d")

    model_comparison_output = model_comparison.copy()
    model_comparison_output[["mae", "rmse", "mape"]] = model_comparison_output[
        ["mae", "rmse", "mape"]
    ].round(2)

    weekly_output.to_csv(WEEKLY_REVENUE_PATH, index=False)
    monthly_output.to_csv(MONTHLY_REVENUE_PATH, index=False)
    model_comparison_output.to_csv(MODEL_COMPARISON_PATH, index=False)
    actual_output.to_csv(ACTUAL_VS_FORECAST_PATH, index=False)
    future_weekly_output.to_csv(FUTURE_WEEKLY_PATH, index=False)
    future_monthly.to_csv(FUTURE_MONTHLY_PATH, index=False)
    business_summary.to_csv(BUSINESS_SUMMARY_PATH, index=False)
    recommendations.to_csv(RECOMMENDATIONS_PATH, index=False)

    return [
        WEEKLY_REVENUE_PATH,
        MONTHLY_REVENUE_PATH,
        MODEL_COMPARISON_PATH,
        ACTUAL_VS_FORECAST_PATH,
        FUTURE_WEEKLY_PATH,
        FUTURE_MONTHLY_PATH,
        BUSINESS_SUMMARY_PATH,
        RECOMMENDATIONS_PATH,
    ]


def replace_forecasting_tables(
    connection: sqlite3.Connection,
    weekly: pd.DataFrame,
    future_weekly: pd.DataFrame,
    future_monthly: pd.DataFrame,
    model_comparison: pd.DataFrame,
) -> dict[str, int]:
    """Replace only the Stage 4 forecasting-related SQLite tables."""
    connection.execute("DROP TABLE IF EXISTS weekly_revenue;")
    connection.execute("DROP TABLE IF EXISTS revenue_forecasts;")
    connection.execute("DROP TABLE IF EXISTS forecast_model_comparison;")

    weekly_table = weekly.copy()
    weekly_table["week_start_date"] = weekly_table["week_start_date"].dt.strftime("%Y-%m-%d")
    weekly_table = weekly_table.round(
        {
            "total_revenue": 2,
            "total_quantity": 2,
            "average_order_value": 2,
        }
    )

    weekly_forecast_table = future_weekly.copy()
    weekly_forecast_table["forecast_type"] = "weekly"
    weekly_forecast_table["forecast_period"] = weekly_forecast_table[
        "week_start_date"
    ].dt.strftime("%Y-%m-%d")
    weekly_forecast_table["forecast_period_start"] = weekly_forecast_table[
        "week_start_date"
    ].dt.strftime("%Y-%m-%d")
    weekly_forecast_table = weekly_forecast_table[
        ["forecast_type", "forecast_period", "forecast_period_start", "forecast_revenue", "model_used"]
    ]

    future_months = pd.to_datetime(future_monthly["forecast_month"] + "-01")
    monthly_forecast_table = future_monthly.copy()
    monthly_forecast_table["forecast_type"] = "monthly"
    monthly_forecast_table["forecast_period"] = monthly_forecast_table["forecast_month"]
    monthly_forecast_table["forecast_period_start"] = future_months.dt.strftime("%Y-%m-%d")
    monthly_forecast_table = monthly_forecast_table[
        ["forecast_type", "forecast_period", "forecast_period_start", "forecast_revenue", "model_used"]
    ]

    revenue_forecasts = pd.concat([weekly_forecast_table, monthly_forecast_table], ignore_index=True)
    comparison_table = model_comparison.copy()
    comparison_table[["mae", "rmse", "mape"]] = comparison_table[["mae", "rmse", "mape"]].round(2)

    weekly_table.to_sql("weekly_revenue", connection, if_exists="replace", index=False)
    revenue_forecasts.to_sql("revenue_forecasts", connection, if_exists="replace", index=False)
    comparison_table.to_sql("forecast_model_comparison", connection, if_exists="replace", index=False)
    connection.commit()

    return {
        "weekly_revenue": int(connection.execute("SELECT COUNT(*) FROM weekly_revenue").fetchone()[0]),
        "revenue_forecasts": int(connection.execute("SELECT COUNT(*) FROM revenue_forecasts").fetchone()[0]),
        "forecast_model_comparison": int(
            connection.execute("SELECT COUNT(*) FROM forecast_model_comparison").fetchone()[0]
        ),
    }


def main() -> None:
    print("Starting Stage 4 revenue forecasting...")
    require_database()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        validate_sales_transactions_table(connection)

        print("Loading valid positive sales records from sales_transactions...")
        sales = load_sales_transactions(connection)

        print("Aggregating weekly and monthly revenue...")
        weekly = aggregate_weekly_revenue(sales)
        monthly = aggregate_monthly_revenue(sales)
        train, test = split_train_test(weekly)

        print("Training and evaluating forecasting models...")
        model_comparison, actual_vs_forecast, best_model = build_model_outputs(weekly, train, test)
        print(f"Best model selected by lowest MAE: {best_model}")

        print("Generating future weekly and monthly forecasts...")
        future_weekly, future_monthly = build_future_forecasts(weekly, monthly, best_model)
        forecast_direction = classify_forecast_direction(weekly, future_weekly)
        business_summary = build_business_summary(
            weekly,
            future_weekly,
            future_monthly,
            model_comparison,
            best_model,
            forecast_direction,
        )
        recommendations = build_recommendations(forecast_direction)

        print("Saving forecasting CSV outputs...")
        output_files = save_csv_outputs(
            weekly,
            monthly,
            model_comparison,
            actual_vs_forecast,
            future_weekly,
            future_monthly,
            business_summary,
            recommendations,
        )

        print("Creating or replacing forecasting-related SQLite tables only...")
        table_counts = replace_forecasting_tables(
            connection,
            weekly,
            future_weekly,
            future_monthly,
            model_comparison,
        )

    best_row = model_comparison[model_comparison["model_name"] == best_model].iloc[0]
    next_8_weeks_total = round(float(future_weekly["forecast_revenue"].sum()), 2)
    next_3_months_total = round(float(future_monthly["forecast_revenue"].sum()), 2)

    print("\nFinal forecasting validation")
    print(f"Number of weekly periods: {len(weekly):,}")
    print(f"Number of monthly periods: {len(monthly):,}")
    print(f"Train weeks: {len(train):,}")
    print(f"Test weeks: {len(test):,}")
    print(f"Best model: {best_model}")
    print(f"MAE: {float(best_row['mae']):,.2f}")
    print(f"RMSE: {float(best_row['rmse']):,.2f}")
    print(f"MAPE: {float(best_row['mape']):,.2f}")
    print(f"Next 8 weeks forecast total: {next_8_weeks_total:,.2f}")
    print(f"Next 3 months forecast total: {next_3_months_total:,.2f}")
    print(f"Forecast direction: {forecast_direction}")
    print(f"Number of forecast output files created: {sum(path.exists() for path in output_files)}")
    for table_name, row_count in table_counts.items():
        print(f"{table_name} row count: {row_count:,}")
    print("Monthly forecast warning: only 13 monthly observations exist, so monthly forecasts are directional business estimates.")
    print("Stage 4 revenue forecasting completed.")


if __name__ == "__main__":
    main()
