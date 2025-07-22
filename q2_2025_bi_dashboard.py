import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dashboard_data_processor import RentRollProcessor
from dashboard_components import DashboardComponents
import pandas as pd
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load and process data
processor = RentRollProcessor()
processor.load_data()

# Calculate metrics for both funds
fund2_metrics = processor.calculate_fund_metrics('Fund 2')
fund3_metrics = processor.calculate_fund_metrics('Fund 3')

# Generate insights
fund2_insights = processor.generate_insights('Fund 2', fund2_metrics)
fund3_insights = processor.generate_insights('Fund 3', fund3_metrics)

# Create dashboard components
components = DashboardComponents()

def create_fund_dashboard(fund_name, metrics, insights):
    """Create a complete dashboard for a specific fund"""
    
    q2_metrics = metrics['Q2_2025']
    q2_summary = metrics['q2_summary']
    
    # KPI Cards Row
    kpi_row = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_kpi_card(
                    "Occupancy Rate",
                    q2_metrics['occupancy_rate'],
                    delta=q2_summary['occupancy_change'],
                    delta_text=f"vs Q1 2025",
                    color='green' if q2_summary['occupancy_change'] > 0 else 'red'
                ),
                config={'displayModeBar': False}
            )
        ], width=3),
        dbc.Col([
            dcc.Graph(
                figure=components.create_kpi_card(
                    "Annual Revenue",
                    q2_metrics['annual_revenue'] / 1e6,
                    delta=q2_summary['revenue_change'],
                    delta_text=f"{q2_summary['revenue_change']:+.1f}% Q/Q",
                    color='#2E86AB'
                ),
                config={'displayModeBar': False}
            )
        ], width=3),
        dbc.Col([
            dcc.Graph(
                figure=components.create_kpi_card(
                    "WALT (months)",
                    q2_metrics['walt'],
                    delta=q2_summary['walt_change'],
                    delta_text=f"vs Q1 2025",
                    color='orange' if q2_metrics['walt'] < 36 else 'green'
                ),
                config={'displayModeBar': False}
            )
        ], width=3),
        dbc.Col([
            dcc.Graph(
                figure=components.create_kpi_card(
                    "Vacant SF",
                    q2_metrics['vacant_sf'] / 1e6,
                    delta=(q2_metrics['vacant_sf'] - metrics['Q1_2025']['vacant_sf']) / 1e6,
                    delta_text="vs Q1 2025 (M)",
                    color='red' if q2_metrics['vacant_sf'] > metrics['Q1_2025']['vacant_sf'] else 'green'
                ),
                config={'displayModeBar': False}
            )
        ], width=3)
    ], className="mb-4")
    
    # Main Charts Row 1
    charts_row1 = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_occupancy_trend(metrics),
                config={'displayModeBar': False}
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                figure=components.create_revenue_waterfall(metrics),
                config={'displayModeBar': False}
            )
        ], width=6)
    ], className="mb-4")
    
    # Main Charts Row 2
    charts_row2 = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_lease_expiry_chart(metrics['expiry_analysis']),
                config={'displayModeBar': False}
            )
        ], width=8),
        dbc.Col([
            dcc.Graph(
                figure=components.create_risk_gauge(metrics['risk_metrics']['overall_risk_score']),
                config={'displayModeBar': False}
            )
        ], width=4)
    ], className="mb-4")
    
    # Additional Charts Row
    charts_row3 = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_property_heatmap(metrics['top_properties']),
                config={'displayModeBar': False}
            )
        ], width=12)
    ], className="mb-4")
    
    charts_row4 = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_tenant_concentration_donut(metrics),
                config={'displayModeBar': False}
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                figure=components.create_leasing_velocity_chart(metrics),
                config={'displayModeBar': False}
            )
        ], width=6)
    ], className="mb-4")
    
    # Summary Table
    table_row = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=components.create_quarterly_comparison_table(metrics),
                config={'displayModeBar': False}
            )
        ], width=12)
    ], className="mb-4")
    
    # Insights Section
    insights_section = dbc.Row([
        dbc.Col([
            html.H3("Key Insights & Recommendations", className="mb-3"),
            html.Div(
                [dbc.Alert(
                    [
                        html.H4(insight['category'], className="alert-heading"),
                        html.P(insight['message']),
                        html.Hr(),
                        html.P(f"Recommendation: {insight['recommendation']}", className="mb-0")
                    ],
                    color=insight['type'],
                    className="mb-3"
                ) for insight in insights]
            )
        ], width=12)
    ])
    
    # Q2 Performance Summary Card
    summary_card = dbc.Card([
        dbc.CardBody([
            html.H4(f"{fund_name} - Q2 2025 Performance Summary", className="card-title"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Net Absorption: "),
                        f"{q2_summary['net_absorption']:+,.0f} SF"
                    ]),
                    html.P([
                        html.Strong("New Leases: "),
                        f"{q2_summary['new_leases']}"
                    ]),
                    html.P([
                        html.Strong("Lost Leases: "),
                        f"{q2_summary['lost_leases']}"
                    ])
                ], width=4),
                dbc.Col([
                    html.P([
                        html.Strong("Avg Rent/SF: "),
                        f"${q2_metrics['avg_rent_psf']:.2f}"
                    ]),
                    html.P([
                        html.Strong("Near-term Expiry: "),
                        f"{q2_metrics['near_term_expiry_pct']:.1f}% of occupied SF"
                    ]),
                    html.P([
                        html.Strong("Risk Level: "),
                        html.Span(
                            metrics['risk_metrics']['risk_level'],
                            style={'color': 'red' if metrics['risk_metrics']['risk_level'] == 'High' 
                                         else 'orange' if metrics['risk_metrics']['risk_level'] == 'Medium' 
                                         else 'green'}
                        )
                    ])
                ], width=4),
                dbc.Col([
                    html.P([
                        html.Strong("Total Properties: "),
                        f"{q2_metrics['properties']}"
                    ]),
                    html.P([
                        html.Strong("Unique Tenants: "),
                        f"{metrics['risk_metrics']['unique_tenants']}"
                    ]),
                    html.P([
                        html.Strong("Monthly Revenue: "),
                        f"${q2_metrics['monthly_revenue']:,.0f}"
                    ])
                ], width=4)
            ])
        ])
    ], className="mb-4")
    
    # Combine all components
    return html.Div([
        summary_card,
        kpi_row,
        charts_row1,
        charts_row2,
        charts_row3,
        charts_row4,
        table_row,
        insights_section
    ])

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Q2 2025 Performance Dashboard", className="text-center mb-4"),
            html.H3("Faropoint Rent Roll Analysis", className="text-center text-muted mb-4"),
            html.Hr()
        ], width=12)
    ]),
    
    dcc.Tabs(id="fund-tabs", value='fund2', children=[
        dcc.Tab(
            label='Fund 2 Dashboard',
            value='fund2',
            children=[
                html.Div(
                    create_fund_dashboard('Fund 2', fund2_metrics, fund2_insights),
                    className="mt-4"
                )
            ]
        ),
        dcc.Tab(
            label='Fund 3 Dashboard',
            value='fund3',
            children=[
                html.Div(
                    create_fund_dashboard('Fund 3', fund3_metrics, fund3_insights),
                    className="mt-4"
                )
            ]
        ),
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P(
                f"Dashboard generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                className="text-center text-muted"
            )
        ], width=12)
    ], className="mt-5")
    
], fluid=True)

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f8f9fa;
            }
            .card {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .card:hover {
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }
            .alert {
                border-left: 5px solid;
            }
            .tab-content {
                padding-top: 20px;
            }
            h1, h2, h3, h4 {
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("Starting Q2 2025 BI Dashboard...")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("\nPress Ctrl+C to stop the server.")
    app.run_server(debug=True)