# Power BI DAX Measures

Create a dedicated table named `Measures` in Power BI and store these measures there. The formulas reference the dashboard-ready CSV table names after import.

## Executive KPI Measures

```DAX
Total Revenue =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "total_revenue"
    )
)
```

```DAX
Total Orders =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "total_orders"
    )
)
```

```DAX
Total Customers =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "total_customers"
    )
)
```

```DAX
Average Order Value =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "average_order_value"
    )
)
```

```DAX
Repeat Customer Rate =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "repeat_customer_rate"
    )
)
```

```DAX
Cancellation Rate =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "cancellation_rate"
    )
)
```

```DAX
Revenue Lost From Cancellations =
VALUE(
    LOOKUPVALUE(
        dashboard_kpi_summary[value],
        dashboard_kpi_summary[metric],
        "estimated_revenue_lost_from_cancellations_returns"
    )
)
```

## Customer Segmentation Measures

```DAX
Customer Count =
SUM(dashboard_segment_summary[customer_count])
```

```DAX
Revenue by Segment =
SUM(dashboard_segment_summary[total_revenue])
```

```DAX
Champion Revenue Share =
DIVIDE(
    CALCULATE(
        [Revenue by Segment],
        dashboard_segment_summary[customer_segment] = "Champions"
    ),
    CALCULATE(
        [Revenue by Segment],
        ALL(dashboard_segment_summary)
    )
)
```

## Forecast Measures

```DAX
Forecast Next 8 Weeks Revenue =
SUM(dashboard_future_weekly_forecast[forecast_revenue])
```

```DAX
Forecast Next 3 Months Revenue =
SUM(dashboard_future_monthly_forecast[forecast_revenue])
```

## Trend And Share Measures

```DAX
Revenue Growth % =
VAR LatestMonth =
    MAX(dashboard_monthly_sales[invoice_year_month])
VAR PreviousMonth =
    CALCULATE(
        MAX(dashboard_monthly_sales[invoice_year_month]),
        FILTER(
            ALL(dashboard_monthly_sales),
            dashboard_monthly_sales[invoice_year_month] < LatestMonth
        )
    )
VAR LatestRevenue =
    CALCULATE(
        SUM(dashboard_monthly_sales[total_revenue]),
        dashboard_monthly_sales[invoice_year_month] = LatestMonth
    )
VAR PreviousRevenue =
    CALCULATE(
        SUM(dashboard_monthly_sales[total_revenue]),
        dashboard_monthly_sales[invoice_year_month] = PreviousMonth
    )
RETURN
    DIVIDE(LatestRevenue - PreviousRevenue, PreviousRevenue)
```

```DAX
Revenue Share % =
DIVIDE(
    SUM(dashboard_country_performance[total_revenue]),
    CALCULATE(
        SUM(dashboard_country_performance[total_revenue]),
        ALL(dashboard_country_performance)
    )
)
```

## Formatting Guidance

- Format revenue measures as currency.
- Format rates and shares as percentages.
- Format order and customer counts as whole numbers.
- Keep measure names business-friendly because they will appear in visuals.
