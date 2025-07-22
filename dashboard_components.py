import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

class DashboardComponents:
    """Reusable components for the BI dashboard"""
    
    @staticmethod
    def create_kpi_card(title, value, delta=None, delta_text=None, color='#1f77b4'):
        """Create a KPI indicator card"""
        fig = go.Figure()
        
        # Add main value
        fig.add_trace(go.Indicator(
            mode="number+delta" if delta is not None else "number",
            value=value,
            delta={'reference': value - delta if delta else None, 
                   'relative': True,
                   'valueformat': '.1f'} if delta else None,
            title={'text': f"<b>{title}</b><br><span style='font-size:0.8em'>{delta_text or ''}</span>"},
            number={'font': {'size': 40, 'color': color}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(
            height=150,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_occupancy_trend(metrics):
        """Create occupancy trend chart"""
        periods = ['Q4 2024', 'Q1 2025', 'Q2 2025']
        occupancy_rates = [
            metrics['Q4_2024']['occupancy_rate'],
            metrics['Q1_2025']['occupancy_rate'],
            metrics['Q2_2025']['occupancy_rate']
        ]
        
        fig = go.Figure()
        
        # Add occupancy line
        fig.add_trace(go.Scatter(
            x=periods,
            y=occupancy_rates,
            mode='lines+markers',
            name='Occupancy Rate',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=10),
            text=[f'{rate:.1f}%' for rate in occupancy_rates],
            textposition='top center'
        ))
        
        # Add target line
        fig.add_hline(y=95, line_dash="dash", line_color="green", 
                      annotation_text="Target: 95%", annotation_position="right")
        
        fig.update_layout(
            title='Occupancy Rate Trend',
            xaxis_title='Quarter',
            yaxis_title='Occupancy Rate (%)',
            height=350,
            yaxis=dict(range=[80, 100]),
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_revenue_waterfall(metrics):
        """Create revenue waterfall chart"""
        q1_rev = metrics['Q1_2025']['annual_revenue'] / 1e6
        q2_rev = metrics['Q2_2025']['annual_revenue'] / 1e6
        change = q2_rev - q1_rev
        
        fig = go.Figure()
        
        fig.add_trace(go.Waterfall(
            x=['Q1 2025', 'Change', 'Q2 2025'],
            y=[q1_rev, change, None],
            measure=['absolute', 'relative', 'total'],
            text=[f'${q1_rev:.1f}M', f'{change:+.1f}M', f'${q2_rev:.1f}M'],
            textposition='auto',
            connector={'line': {'color': 'rgb(63, 63, 63)'}},
            increasing={'marker': {'color': 'green'}},
            decreasing={'marker': {'color': 'red'}},
            totals={'marker': {'color': '#2E86AB'}}
        ))
        
        fig.update_layout(
            title='Q2 2025 Revenue Change Analysis',
            yaxis_title='Annual Revenue ($M)',
            height=350,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_lease_expiry_chart(expiry_data):
        """Create lease expiration timeline"""
        periods = list(expiry_data.keys())
        sf_values = [expiry_data[p]['sf'] / 1e6 for p in periods]
        rent_values = [expiry_data[p]['annual_rent'] / 1e6 for p in periods]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Expiring Square Feet', 'Expiring Annual Rent'),
            horizontal_spacing=0.15
        )
        
        # SF bar chart
        fig.add_trace(
            go.Bar(x=periods, y=sf_values, name='SF (Millions)',
                   marker_color='#A23B72', text=[f'{v:.1f}M' for v in sf_values],
                   textposition='auto'),
            row=1, col=1
        )
        
        # Rent bar chart
        fig.add_trace(
            go.Bar(x=periods, y=rent_values, name='Rent ($M)',
                   marker_color='#F18F01', text=[f'${v:.1f}M' for v in rent_values],
                   textposition='auto'),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Lease Expiration Schedule',
            height=350,
            showlegend=False
        )
        
        fig.update_xaxes(tickangle=-45)
        
        return fig
    
    @staticmethod
    def create_property_heatmap(top_properties):
        """Create property performance heatmap"""
        df = pd.DataFrame(top_properties)
        
        # Create a matrix for the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=[[prop['annual_rent']/1e6 for prop in top_properties]],
            x=[prop['property'][:20] for prop in top_properties],
            y=['Annual Rent ($M)'],
            colorscale='Blues',
            text=[[f"${prop['annual_rent']/1e6:.2f}M<br>{prop['total_sf']:,.0f} SF" 
                   for prop in top_properties]],
            texttemplate="%{text}",
            textfont={"size": 10},
            showscale=True
        ))
        
        fig.update_layout(
            title='Top 10 Properties by Revenue',
            height=200,
            xaxis={'side': 'bottom'},
            margin=dict(l=100, r=20, t=50, b=100)
        )
        
        fig.update_xaxes(tickangle=-45)
        
        return fig
    
    @staticmethod
    def create_risk_gauge(risk_score):
        """Create risk assessment gauge"""
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_tenant_concentration_donut(metrics):
        """Create tenant concentration donut chart"""
        top_5 = metrics['risk_metrics']['top_5_concentration']
        top_10 = metrics['risk_metrics']['top_10_concentration'] - top_5
        other = 100 - metrics['risk_metrics']['top_10_concentration']
        
        fig = go.Figure(data=[go.Pie(
            labels=['Top 5 Tenants', 'Next 5 Tenants', 'Other Tenants'],
            values=[top_5, top_10, other],
            hole=.3,
            marker_colors=['#E63946', '#F77F00', '#06D6A0']
        )])
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
        
        fig.update_layout(
            title='Tenant Concentration',
            height=350,
            annotations=[dict(text=f"{metrics['risk_metrics']['unique_tenants']}<br>Tenants", 
                            x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    @staticmethod
    def create_quarterly_comparison_table(metrics):
        """Create quarterly metrics comparison table"""
        data = []
        
        for period in ['Q4_2024', 'Q1_2025', 'Q2_2025']:
            m = metrics[period]
            data.append([
                period.replace('_', ' '),
                f"{m['occupancy_rate']:.1f}%",
                f"${m['annual_revenue']/1e6:.1f}M",
                f"${m['avg_rent_psf']:.2f}",
                f"{m['walt']:.1f}",
                f"{m['vacant_sf']:,.0f}"
            ])
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Period</b>', '<b>Occupancy</b>', '<b>Revenue</b>', 
                       '<b>Avg Rent/SF</b>', '<b>WALT (mo)</b>', '<b>Vacant SF</b>'],
                fill_color='#2E86AB',
                font=dict(color='white', size=12),
                align='center'
            ),
            cells=dict(
                values=list(zip(*data)),
                fill_color='lavender',
                align='center',
                height=30
            )
        )])
        
        fig.update_layout(
            title='Quarterly Performance Summary',
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_leasing_velocity_chart(metrics):
        """Create leasing velocity chart"""
        periods = ['Q1 2025', 'Q2 2025']
        new_leases = [
            metrics['Q1_2025']['occupied_leases'] - metrics['Q4_2024']['occupied_leases'],
            metrics['q2_summary']['new_leases']
        ]
        lost_leases = [
            metrics['Q4_2024']['occupied_leases'] - metrics['Q1_2025']['occupied_leases'],
            metrics['q2_summary']['lost_leases']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=periods,
            y=new_leases,
            name='New Leases',
            marker_color='green',
            text=[f'+{v}' for v in new_leases],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=periods,
            y=[-l for l in lost_leases],
            name='Lost Leases',
            marker_color='red',
            text=[f'-{v}' for v in lost_leases],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Quarterly Leasing Activity',
            yaxis_title='Number of Leases',
            barmode='relative',
            height=350,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_insight_cards(insights):
        """Create HTML cards for insights"""
        html_cards = []
        
        colors = {
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8'
        }
        
        for insight in insights:
            color = colors.get(insight['type'], '#6c757d')
            card_html = f"""
            <div style="background-color: {color}; color: white; padding: 15px; 
                        margin: 10px 0; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0;">{insight['category']}</h4>
                <p style="margin: 0 0 10px 0;">{insight['message']}</p>
                <p style="margin: 0; font-style: italic;">
                    <strong>Recommendation:</strong> {insight['recommendation']}
                </p>
            </div>
            """
            html_cards.append(card_html)
        
        return ''.join(html_cards)