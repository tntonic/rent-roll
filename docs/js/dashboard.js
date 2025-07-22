// Rent Roll BI Dashboard JavaScript
let dashboardData = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// Load dashboard data from JSON
async function loadDashboardData() {
    try {
        const response = await fetch('data/dashboard_data.json');
        dashboardData = await response.json();
        
        // Update generated date
        document.getElementById('generated-date').textContent = dashboardData.metadata.generated_date;
        
        // Initialize dashboards
        initializeFundDashboard('fund2', dashboardData.fund2);
        initializeFundDashboard('fund3', dashboardData.fund3);
        initializeComparison();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Failed to load dashboard data');
    }
}

// Initialize fund dashboard
function initializeFundDashboard(fundKey, fundData) {
    const contentDiv = document.getElementById(`${fundKey}-content`);
    const fundName = fundKey === 'fund2' ? 'Fund 2' : 'Fund 3';
    
    const html = `
        <!-- Fund Summary Section -->
        <div class="summary-section">
            <div class="row">
                <div class="col-md-8">
                    <h2><i class="fas fa-building"></i> ${fundName} - Q2 2025 Performance Summary</h2>
                    <p class="text-muted">Quarter-over-quarter performance metrics and insights</p>
                </div>
                <div class="col-md-4 text-end">
                    <span class="risk-badge ${getRiskClass(fundData.metrics.risk_metrics.risk_level)}">
                        ${fundData.metrics.risk_metrics.risk_level} Risk
                    </span>
                </div>
            </div>
            <hr>
            <div class="row">
                <div class="col-md-4">
                    <div class="metric-row">
                        <span class="metric-label">Portfolio Size:</span>
                        <span class="metric-value">${formatNumber(fundData.metrics.Q2_2025.total_sf)} SF</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Properties:</span>
                        <span class="metric-value">${fundData.metrics.Q2_2025.properties}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Unique Tenants:</span>
                        <span class="metric-value">${fundData.metrics.risk_metrics.unique_tenants}</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-row">
                        <span class="metric-label">Net Absorption:</span>
                        <span class="metric-value ${fundData.metrics.q2_summary.net_absorption > 0 ? 'text-success' : 'text-danger'}">
                            ${formatNumber(fundData.metrics.q2_summary.net_absorption)} SF
                        </span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">New Leases Q2:</span>
                        <span class="metric-value">${fundData.metrics.q2_summary.new_leases}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Lost Leases Q2:</span>
                        <span class="metric-value">${fundData.metrics.q2_summary.lost_leases}</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-row">
                        <span class="metric-label">Monthly Revenue:</span>
                        <span class="metric-value">$${formatNumber(fundData.metrics.Q2_2025.monthly_revenue)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Annual Revenue:</span>
                        <span class="metric-value">$${formatNumber(fundData.metrics.Q2_2025.annual_revenue)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Avg Rent/SF:</span>
                        <span class="metric-value">$${fundData.metrics.Q2_2025.avg_rent_psf.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="row">
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <div class="kpi-label">Occupancy Rate</div>
                    <div class="kpi-value" style="color: ${fundData.metrics.Q2_2025.occupancy_rate > 90 ? '#28a745' : '#dc3545'}">
                        ${fundData.metrics.Q2_2025.occupancy_rate.toFixed(1)}%
                    </div>
                    <div class="kpi-delta ${fundData.metrics.q2_summary.occupancy_change > 0 ? 'positive' : 'negative'}">
                        ${fundData.metrics.q2_summary.occupancy_change > 0 ? '↑' : '↓'} ${Math.abs(fundData.metrics.q2_summary.occupancy_change).toFixed(1)}pp vs Q1
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <div class="kpi-label">WALT (months)</div>
                    <div class="kpi-value" style="color: ${fundData.metrics.Q2_2025.walt > 36 ? '#28a745' : '#ffc107'}">
                        ${fundData.metrics.Q2_2025.walt.toFixed(1)}
                    </div>
                    <div class="kpi-delta ${fundData.metrics.q2_summary.walt_change > 0 ? 'positive' : 'negative'}">
                        ${fundData.metrics.q2_summary.walt_change > 0 ? '↑' : '↓'} ${Math.abs(fundData.metrics.q2_summary.walt_change).toFixed(1)} vs Q1
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <div class="kpi-label">Revenue Change</div>
                    <div class="kpi-value" style="color: ${fundData.metrics.q2_summary.revenue_change > 0 ? '#28a745' : '#dc3545'}">
                        ${fundData.metrics.q2_summary.revenue_change > 0 ? '+' : ''}${fundData.metrics.q2_summary.revenue_change.toFixed(1)}%
                    </div>
                    <div class="kpi-delta">
                        Q2 vs Q1 2025
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <div class="kpi-label">Vacant SF</div>
                    <div class="kpi-value" style="color: #dc3545">
                        ${formatNumber(fundData.metrics.Q2_2025.vacant_sf / 1000000, 1)}M
                    </div>
                    <div class="kpi-delta negative">
                        ${fundData.metrics.Q2_2025.vacant_sf > fundData.metrics.Q1_2025.vacant_sf ? '↑' : '↓'} ${formatNumber(Math.abs(fundData.metrics.Q2_2025.vacant_sf - fundData.metrics.Q1_2025.vacant_sf))} vs Q1
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row 1 -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="${fundKey}-occupancy-trend"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="${fundKey}-revenue-trend"></div>
                </div>
            </div>
        </div>

        <!-- Charts Row 2 -->
        <div class="row">
            <div class="col-md-8">
                <div class="chart-container">
                    <div id="${fundKey}-expiry-analysis"></div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="chart-container">
                    <div id="${fundKey}-risk-gauge"></div>
                </div>
            </div>
        </div>

        <!-- Charts Row 3 -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="${fundKey}-tenant-concentration"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="${fundKey}-top-properties"></div>
                </div>
            </div>
        </div>

        <!-- Insights Section -->
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <h4><i class="fas fa-lightbulb"></i> Key Insights & Recommendations</h4>
                    <div id="${fundKey}-insights">
                        ${fundData.insights.map(insight => `
                            <div class="insight-card ${insight.type}">
                                <h5><i class="fas fa-info-circle"></i> ${insight.category}</h5>
                                <p><strong>Finding:</strong> ${insight.message}</p>
                                <p><strong>Recommendation:</strong> ${insight.recommendation}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Create charts
    createOccupancyTrend(fundKey, fundData);
    createRevenueTrend(fundKey, fundData);
    createExpiryAnalysis(fundKey, fundData);
    createRiskGauge(fundKey, fundData);
    createTenantConcentration(fundKey, fundData);
    createTopProperties(fundKey, fundData);
}

// Create occupancy trend chart
function createOccupancyTrend(fundKey, fundData) {
    const data = [{
        x: ['Q4 2024', 'Q1 2025', 'Q2 2025'],
        y: [
            fundData.metrics.Q4_2024.occupancy_rate,
            fundData.metrics.Q1_2025.occupancy_rate,
            fundData.metrics.Q2_2025.occupancy_rate
        ],
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#2E86AB', width: 3 },
        marker: { size: 10 }
    }];
    
    const layout = {
        title: 'Occupancy Rate Trend',
        xaxis: { title: 'Quarter' },
        yaxis: { title: 'Occupancy Rate (%)', range: [80, 100] },
        shapes: [{
            type: 'line',
            x0: 0, x1: 1, xref: 'paper',
            y0: 95, y1: 95,
            line: { color: 'green', width: 2, dash: 'dash' }
        }],
        annotations: [{
            x: 1, y: 95,
            text: 'Target: 95%',
            showarrow: false,
            xanchor: 'left'
        }]
    };
    
    Plotly.newPlot(`${fundKey}-occupancy-trend`, data, layout, {responsive: true});
}

// Create revenue trend chart
function createRevenueTrend(fundKey, fundData) {
    const data = [{
        x: ['Q4 2024', 'Q1 2025', 'Q2 2025'],
        y: [
            fundData.metrics.Q4_2024.annual_revenue / 1000000,
            fundData.metrics.Q1_2025.annual_revenue / 1000000,
            fundData.metrics.Q2_2025.annual_revenue / 1000000
        ],
        type: 'bar',
        marker: { color: '#2E86AB' }
    }];
    
    const layout = {
        title: 'Annual Revenue Trend',
        xaxis: { title: 'Quarter' },
        yaxis: { title: 'Annual Revenue ($M)' }
    };
    
    Plotly.newPlot(`${fundKey}-revenue-trend`, data, layout, {responsive: true});
}

// Create expiry analysis chart
function createExpiryAnalysis(fundKey, fundData) {
    const periods = Object.keys(fundData.metrics.expiry_analysis);
    const sf_values = periods.map(p => fundData.metrics.expiry_analysis[p].sf / 1000000);
    const rent_values = periods.map(p => fundData.metrics.expiry_analysis[p].annual_rent / 1000000);
    
    const data = [
        {
            x: periods,
            y: sf_values,
            type: 'bar',
            name: 'SF (Millions)',
            marker: { color: '#A23B72' },
            yaxis: 'y'
        },
        {
            x: periods,
            y: rent_values,
            type: 'bar',
            name: 'Rent ($M)',
            marker: { color: '#F18F01' },
            yaxis: 'y2'
        }
    ];
    
    const layout = {
        title: 'Lease Expiration Schedule',
        xaxis: { title: 'Expiration Period' },
        yaxis: { title: 'Square Feet (Millions)', side: 'left' },
        yaxis2: { title: 'Annual Rent ($M)', side: 'right', overlaying: 'y' },
        legend: { x: 0.7, y: 1 }
    };
    
    Plotly.newPlot(`${fundKey}-expiry-analysis`, data, layout, {responsive: true});
}

// Create risk gauge
function createRiskGauge(fundKey, fundData) {
    const data = [{
        type: 'indicator',
        mode: 'gauge+number',
        value: fundData.metrics.risk_metrics.overall_risk_score,
        title: { text: 'Overall Risk Score' },
        gauge: {
            axis: { range: [0, 100] },
            bar: { color: 'darkblue' },
            steps: [
                { range: [0, 30], color: 'lightgreen' },
                { range: [30, 60], color: 'yellow' },
                { range: [60, 100], color: 'lightcoral' }
            ]
        }
    }];
    
    const layout = {
        height: 300,
        margin: { t: 25, r: 25, l: 25, b: 25 }
    };
    
    Plotly.newPlot(`${fundKey}-risk-gauge`, data, layout, {responsive: true});
}

// Create tenant concentration donut chart
function createTenantConcentration(fundKey, fundData) {
    const top5 = fundData.metrics.risk_metrics.top_5_concentration;
    const top10 = fundData.metrics.risk_metrics.top_10_concentration - top5;
    const other = 100 - fundData.metrics.risk_metrics.top_10_concentration;
    
    const data = [{
        labels: ['Top 5 Tenants', 'Next 5 Tenants', 'Other Tenants'],
        values: [top5, top10, other],
        type: 'pie',
        hole: 0.3,
        marker: {
            colors: ['#E63946', '#F77F00', '#06D6A0']
        }
    }];
    
    const layout = {
        title: 'Tenant Revenue Concentration',
        annotations: [{
            text: `${fundData.metrics.risk_metrics.unique_tenants}<br>Tenants`,
            x: 0.5, y: 0.5,
            font: { size: 20 },
            showarrow: false
        }]
    };
    
    Plotly.newPlot(`${fundKey}-tenant-concentration`, data, layout, {responsive: true});
}

// Create top properties chart
function createTopProperties(fundKey, fundData) {
    const properties = fundData.metrics.top_properties.slice(0, 10);
    
    const data = [{
        x: properties.map(p => p.annual_rent / 1000000),
        y: properties.map(p => p.property.substring(0, 25)),
        type: 'bar',
        orientation: 'h',
        marker: { color: '#2E86AB' }
    }];
    
    const layout = {
        title: 'Top 10 Properties by Annual Rent',
        xaxis: { title: 'Annual Rent ($M)' },
        yaxis: { title: 'Property' },
        margin: { l: 200 }
    };
    
    Plotly.newPlot(`${fundKey}-top-properties`, data, layout, {responsive: true});
}

// Initialize comparison dashboard
function initializeComparison() {
    const contentDiv = document.getElementById('comparison-content');
    
    const html = `
        <div class="summary-section">
            <h2><i class="fas fa-balance-scale"></i> Fund Comparison - Q2 2025</h2>
            <p class="text-muted">Side-by-side performance analysis</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="comparison-occupancy"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="comparison-revenue"></div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="comparison-walt"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="comparison-risk"></div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <h4><i class="fas fa-chart-bar"></i> Performance Comparison Table</h4>
                    <div id="comparison-table"></div>
                </div>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Create comparison charts
    createComparisonCharts();
}

// Create comparison charts
function createComparisonCharts() {
    if (!dashboardData) return;
    
    // Occupancy comparison
    const occupancyData = [
        {
            x: ['Q4 2024', 'Q1 2025', 'Q2 2025'],
            y: [
                dashboardData.fund2.metrics.Q4_2024.occupancy_rate,
                dashboardData.fund2.metrics.Q1_2025.occupancy_rate,
                dashboardData.fund2.metrics.Q2_2025.occupancy_rate
            ],
            name: 'Fund 2',
            type: 'scatter',
            mode: 'lines+markers'
        },
        {
            x: ['Q4 2024', 'Q1 2025', 'Q2 2025'],
            y: [
                dashboardData.fund3.metrics.Q4_2024.occupancy_rate,
                dashboardData.fund3.metrics.Q1_2025.occupancy_rate,
                dashboardData.fund3.metrics.Q2_2025.occupancy_rate
            ],
            name: 'Fund 3',
            type: 'scatter',
            mode: 'lines+markers'
        }
    ];
    
    Plotly.newPlot('comparison-occupancy', occupancyData, {
        title: 'Occupancy Rate Comparison',
        yaxis: { title: 'Occupancy Rate (%)' }
    }, {responsive: true});
    
    // Revenue comparison
    const revenueData = [
        {
            x: ['Fund 2', 'Fund 3'],
            y: [
                dashboardData.fund2.metrics.Q2_2025.annual_revenue / 1000000,
                dashboardData.fund3.metrics.Q2_2025.annual_revenue / 1000000
            ],
            type: 'bar',
            marker: { color: ['#2E86AB', '#A23B72'] }
        }
    ];
    
    Plotly.newPlot('comparison-revenue', revenueData, {
        title: 'Q2 2025 Annual Revenue',
        yaxis: { title: 'Revenue ($M)' }
    }, {responsive: true});
    
    // WALT comparison
    const waltData = [
        {
            x: ['Fund 2', 'Fund 3'],
            y: [
                dashboardData.fund2.metrics.Q2_2025.walt,
                dashboardData.fund3.metrics.Q2_2025.walt
            ],
            type: 'bar',
            marker: { color: ['#2E86AB', '#A23B72'] }
        }
    ];
    
    Plotly.newPlot('comparison-walt', waltData, {
        title: 'WALT Comparison (Q2 2025)',
        yaxis: { title: 'WALT (months)' }
    }, {responsive: true});
    
    // Risk comparison
    const riskData = [
        {
            x: ['Fund 2', 'Fund 3'],
            y: [
                dashboardData.fund2.metrics.risk_metrics.overall_risk_score,
                dashboardData.fund3.metrics.risk_metrics.overall_risk_score
            ],
            type: 'bar',
            marker: { color: ['#dc3545', '#ffc107'] }
        }
    ];
    
    Plotly.newPlot('comparison-risk', riskData, {
        title: 'Risk Score Comparison',
        yaxis: { title: 'Risk Score (0-100)' }
    }, {responsive: true});
    
    // Create comparison table
    createComparisonTable();
}

// Create comparison table
function createComparisonTable() {
    const tableHtml = `
        <div class="table-responsive">
            <table class="table table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>Metric</th>
                        <th>Fund 2</th>
                        <th>Fund 3</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Occupancy Rate</td>
                        <td>${dashboardData.fund2.metrics.Q2_2025.occupancy_rate.toFixed(1)}%</td>
                        <td>${dashboardData.fund3.metrics.Q2_2025.occupancy_rate.toFixed(1)}%</td>
                        <td class="${dashboardData.fund3.metrics.Q2_2025.occupancy_rate > dashboardData.fund2.metrics.Q2_2025.occupancy_rate ? 'text-success' : 'text-danger'}">
                            ${(dashboardData.fund3.metrics.Q2_2025.occupancy_rate - dashboardData.fund2.metrics.Q2_2025.occupancy_rate).toFixed(1)}pp
                        </td>
                    </tr>
                    <tr>
                        <td>Annual Revenue</td>
                        <td>$${formatNumber(dashboardData.fund2.metrics.Q2_2025.annual_revenue)}</td>
                        <td>$${formatNumber(dashboardData.fund3.metrics.Q2_2025.annual_revenue)}</td>
                        <td class="text-success">+$${formatNumber(dashboardData.fund3.metrics.Q2_2025.annual_revenue - dashboardData.fund2.metrics.Q2_2025.annual_revenue)}</td>
                    </tr>
                    <tr>
                        <td>Average Rent/SF</td>
                        <td>$${dashboardData.fund2.metrics.Q2_2025.avg_rent_psf.toFixed(2)}</td>
                        <td>$${dashboardData.fund3.metrics.Q2_2025.avg_rent_psf.toFixed(2)}</td>
                        <td class="${dashboardData.fund3.metrics.Q2_2025.avg_rent_psf > dashboardData.fund2.metrics.Q2_2025.avg_rent_psf ? 'text-success' : 'text-danger'}">
                            +$${(dashboardData.fund3.metrics.Q2_2025.avg_rent_psf - dashboardData.fund2.metrics.Q2_2025.avg_rent_psf).toFixed(2)}
                        </td>
                    </tr>
                    <tr>
                        <td>WALT (months)</td>
                        <td>${dashboardData.fund2.metrics.Q2_2025.walt.toFixed(1)}</td>
                        <td>${dashboardData.fund3.metrics.Q2_2025.walt.toFixed(1)}</td>
                        <td class="${dashboardData.fund3.metrics.Q2_2025.walt > dashboardData.fund2.metrics.Q2_2025.walt ? 'text-success' : 'text-danger'}">
                            ${dashboardData.fund3.metrics.Q2_2025.walt > dashboardData.fund2.metrics.Q2_2025.walt ? '+' : ''}${(dashboardData.fund3.metrics.Q2_2025.walt - dashboardData.fund2.metrics.Q2_2025.walt).toFixed(1)}
                        </td>
                    </tr>
                    <tr>
                        <td>Risk Score</td>
                        <td>${dashboardData.fund2.metrics.risk_metrics.overall_risk_score}</td>
                        <td>${dashboardData.fund3.metrics.risk_metrics.overall_risk_score}</td>
                        <td class="${dashboardData.fund2.metrics.risk_metrics.overall_risk_score > dashboardData.fund3.metrics.risk_metrics.overall_risk_score ? 'text-success' : 'text-danger'}">
                            ${dashboardData.fund2.metrics.risk_metrics.overall_risk_score > dashboardData.fund3.metrics.risk_metrics.overall_risk_score ? 'Fund 2 Higher Risk' : 'Fund 3 Higher Risk'}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('comparison-table').innerHTML = tableHtml;
}

// Utility functions
function formatNumber(num, decimals = 0) {
    if (num == null) return '0';
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function getRiskClass(riskLevel) {
    switch (riskLevel.toLowerCase()) {
        case 'high':
            return 'risk-high';
        case 'medium':
        case 'medium-high':
            return 'risk-medium';
        default:
            return 'risk-low';
    }
}

function showErrorMessage(message) {
    document.body.innerHTML = `
        <div class="container mt-5">
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error!</h4>
                <p>${message}</p>
            </div>
        </div>
    `;
}