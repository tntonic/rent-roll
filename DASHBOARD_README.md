# Q2 2025 BI Dashboard - User Guide

## Overview
This interactive Business Intelligence dashboard provides comprehensive analysis of Q2 2025 performance for Fund 2 and Fund 3, including visualizations, metrics, insights, and actionable recommendations.

## Features
- **Separate Fund Dashboards**: Dedicated tabs for Fund 2 and Fund 3
- **Interactive Visualizations**: 8+ chart types with hover details
- **Real-time KPIs**: Occupancy, Revenue, WALT, and Vacancy metrics
- **Trend Analysis**: Quarter-over-quarter performance tracking
- **Risk Assessment**: Automated risk scoring and alerts
- **Actionable Insights**: AI-generated recommendations

## Requirements
```bash
pip install dash plotly pandas openpyxl dash-bootstrap-components
```

## Running the Dashboard

1. **Navigate to the directory**:
   ```bash
   cd "/Users/michaeltang/Downloads/Rent Roll"
   ```

2. **Install requirements** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the dashboard**:
   ```bash
   python q2_2025_bi_dashboard.py
   ```

4. **Access the dashboard**:
   - Open your web browser
   - Navigate to: http://127.0.0.1:8050/
   - Dashboard will load automatically

## Dashboard Navigation

### Main Components:
1. **Fund Selection Tabs**: Click tabs to switch between Fund 2 and Fund 3
2. **KPI Cards**: Top-level metrics with Q/Q comparisons
3. **Performance Charts**: Interactive visualizations (hover for details)
4. **Summary Tables**: Quarterly comparison data
5. **Insights Section**: Color-coded alerts and recommendations

### Key Visualizations:
- **Occupancy Trend**: 3-quarter occupancy evolution
- **Revenue Waterfall**: Q2 revenue change breakdown
- **Lease Expiry Timeline**: SF and revenue at risk by period
- **Risk Gauge**: Overall portfolio risk assessment
- **Property Heatmap**: Top 10 properties by revenue
- **Tenant Concentration**: Revenue diversification analysis
- **Leasing Velocity**: New vs lost leases by quarter

## Data Sources
- `Faropoint Rent Roll All Funds (24DEC).xlsx` - Q4 2024 baseline
- `Faropoint Rent Roll All Funds (25MAR).xlsx` - Q1 2025 data
- `Faropoint Rent Roll All Funds (25JUN).xlsx` - Q2 2025 data

## Key Insights Files
- `fund_2_analysis.json` - Detailed Fund 2 analysis and recommendations
- `fund_3_analysis.json` - Detailed Fund 3 analysis and recommendations

## Interpreting the Dashboard

### Risk Levels:
- **Green (Low)**: 0-30 risk score
- **Yellow (Medium)**: 30-60 risk score  
- **Red (High)**: 60-100 risk score

### Insight Types:
- **Success** (Green): Positive developments
- **Warning** (Yellow): Areas needing attention
- **Danger** (Red): Critical issues requiring immediate action
- **Info** (Blue): General observations

## Export Options
- **Screenshots**: Use browser print function for PDF export
- **Data Export**: Right-click on tables to copy data
- **Full Report**: Access JSON analysis files for detailed insights

## Troubleshooting
1. **Port Already in Use**: Change port in `app.run_server(port=8051)`
2. **Missing Data**: Ensure all Excel files are in the same directory
3. **Module Errors**: Install missing packages with pip

## Customization
- Modify `dashboard_components.py` to change chart styles
- Update `dashboard_data_processor.py` to add new metrics
- Edit JSON files to customize recommendations

## Support
For questions or issues, refer to the analysis files or regenerate insights using the data processor.

---
*Dashboard Version 1.0 - Q2 2025 Performance Review*