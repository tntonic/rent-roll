import pandas as pd
import numpy as np
from datetime import datetime
import json

class RentRollProcessor:
    """Process rent roll data for dashboard visualization"""
    
    def __init__(self):
        self.dec_data = None
        self.mar_data = None
        self.jun_data = None
        self.metrics = {}
        
    def load_data(self):
        """Load all three rent roll files"""
        self.dec_data = self._process_rent_roll('Faropoint Rent Roll All Funds (24DEC).xlsx', datetime(2024, 12, 31))
        self.mar_data = self._process_rent_roll('Faropoint Rent Roll All Funds (25MAR).xlsx', datetime(2025, 3, 31))
        self.jun_data = self._process_rent_roll('Faropoint Rent Roll All Funds (25JUN).xlsx', datetime(2025, 6, 30))
        
    def _process_rent_roll(self, file_path, analysis_date):
        """Process individual rent roll file"""
        df = pd.read_excel(file_path, sheet_name='Report1', skiprows=4)
        
        df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
                      'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
                      'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']
        
        df = df.dropna(subset=['Property'])
        df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')
        df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')
        
        df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')
        df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)
        df['Months_To_Expiry'] = df.apply(lambda row: 
            max((row['Lease_To'] - analysis_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
            axis=1)
        
        numeric_cols = ['Area', 'Monthly_Rent', 'Annual_Rent', 'Annual_Rent_Area']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df_valid = df[df['Area'].notna() & (df['Area'] > 0) & df['Fund'].isin(['Fund 2', 'Fund 3'])]
        
        # Add tenant name extraction
        df_valid['Tenant_Name'] = df_valid['Lease'].str.extract(r'^([^(]+)')
        df_valid['Tenant_Name'] = df_valid['Tenant_Name'].str.strip()
        
        return df_valid
    
    def calculate_fund_metrics(self, fund):
        """Calculate comprehensive metrics for a specific fund"""
        metrics = {
            'Q4_2024': self._calculate_period_metrics(self.dec_data, fund, 'Q4 2024'),
            'Q1_2025': self._calculate_period_metrics(self.mar_data, fund, 'Q1 2025'),
            'Q2_2025': self._calculate_period_metrics(self.jun_data, fund, 'Q2 2025')
        }
        
        # Calculate Q2 specific metrics
        q2_data = self.jun_data[self.jun_data['Fund'] == fund]
        mar_data = self.mar_data[self.mar_data['Fund'] == fund]
        
        # Q2 Performance Summary
        metrics['q2_summary'] = {
            'occupancy_change': metrics['Q2_2025']['occupancy_rate'] - metrics['Q1_2025']['occupancy_rate'],
            'revenue_change': ((metrics['Q2_2025']['annual_revenue'] - metrics['Q1_2025']['annual_revenue']) / 
                              metrics['Q1_2025']['annual_revenue'] * 100) if metrics['Q1_2025']['annual_revenue'] > 0 else 0,
            'walt_change': metrics['Q2_2025']['walt'] - metrics['Q1_2025']['walt'],
            'new_leases': self._count_new_leases(mar_data, q2_data),
            'lost_leases': self._count_lost_leases(mar_data, q2_data),
            'net_absorption': metrics['Q2_2025']['occupied_sf'] - metrics['Q1_2025']['occupied_sf']
        }
        
        # Top properties by revenue
        metrics['top_properties'] = self._get_top_properties(q2_data)
        
        # Expiry analysis
        metrics['expiry_analysis'] = self._get_expiry_analysis(q2_data)
        
        # Risk metrics
        metrics['risk_metrics'] = self._calculate_risk_metrics(q2_data, metrics)
        
        return metrics
    
    def _calculate_period_metrics(self, data, fund, period):
        """Calculate metrics for a specific period and fund"""
        fund_data = data[data['Fund'] == fund]
        occupied_data = fund_data[~fund_data['Is_Vacant']]
        
        total_sf = fund_data['Area'].sum()
        occupied_sf = occupied_data['Area'].sum()
        
        walt = 0
        if len(occupied_data) > 0 and occupied_data['Area'].sum() > 0:
            walt = (occupied_data['Area'] * occupied_data['Months_To_Expiry']).sum() / occupied_data['Area'].sum()
        
        return {
            'period': period,
            'properties': fund_data['Prop_Code'].nunique(),
            'total_leases': len(fund_data),
            'occupied_leases': len(occupied_data),
            'vacant_leases': fund_data['Is_Vacant'].sum(),
            'total_sf': total_sf,
            'occupied_sf': occupied_sf,
            'vacant_sf': fund_data[fund_data['Is_Vacant']]['Area'].sum(),
            'occupancy_rate': (occupied_sf / total_sf * 100) if total_sf > 0 else 0,
            'annual_revenue': occupied_data['Annual_Rent'].sum(),
            'monthly_revenue': occupied_data['Monthly_Rent'].sum(),
            'avg_rent_psf': occupied_data['Annual_Rent'].sum() / occupied_sf if occupied_sf > 0 else 0,
            'walt': walt,
            'near_term_expiry_sf': occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum(),
            'near_term_expiry_pct': (occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum() / 
                                     occupied_sf * 100) if occupied_sf > 0 else 0
        }
    
    def _count_new_leases(self, old_data, new_data):
        """Count new leases between periods"""
        old_tenants = set(old_data[~old_data['Is_Vacant']]['Lease'].unique())
        new_tenants = set(new_data[~new_data['Is_Vacant']]['Lease'].unique())
        return len(new_tenants - old_tenants)
    
    def _count_lost_leases(self, old_data, new_data):
        """Count lost leases between periods"""
        old_tenants = set(old_data[~old_data['Is_Vacant']]['Lease'].unique())
        new_tenants = set(new_data[~new_data['Is_Vacant']]['Lease'].unique())
        return len(old_tenants - new_tenants)
    
    def _get_top_properties(self, data, n=10):
        """Get top properties by annual rent"""
        property_summary = data.groupby(['Prop_Code', 'Property']).agg({
            'Area': 'sum',
            'Annual_Rent': 'sum',
            'Is_Vacant': 'sum'
        }).sort_values('Annual_Rent', ascending=False)
        
        top_props = []
        for idx, row in property_summary.head(n).iterrows():
            prop_name = idx[1].split('(')[0].strip()
            top_props.append({
                'property': prop_name,
                'prop_code': idx[0],
                'total_sf': row['Area'],
                'annual_rent': row['Annual_Rent'],
                'has_vacancy': row['Is_Vacant'] > 0
            })
        
        return top_props
    
    def _get_expiry_analysis(self, data):
        """Analyze lease expirations"""
        occupied_data = data[~data['Is_Vacant']]
        
        buckets = {
            '0-6 months': occupied_data[(occupied_data['Months_To_Expiry'] > 0) & 
                                       (occupied_data['Months_To_Expiry'] <= 6)],
            '6-12 months': occupied_data[(occupied_data['Months_To_Expiry'] > 6) & 
                                        (occupied_data['Months_To_Expiry'] <= 12)],
            '12-24 months': occupied_data[(occupied_data['Months_To_Expiry'] > 12) & 
                                         (occupied_data['Months_To_Expiry'] <= 24)],
            '24-36 months': occupied_data[(occupied_data['Months_To_Expiry'] > 24) & 
                                         (occupied_data['Months_To_Expiry'] <= 36)],
            '36+ months': occupied_data[occupied_data['Months_To_Expiry'] > 36]
        }
        
        expiry_data = {}
        for period, df in buckets.items():
            expiry_data[period] = {
                'count': len(df),
                'sf': df['Area'].sum(),
                'annual_rent': df['Annual_Rent'].sum()
            }
        
        return expiry_data
    
    def _calculate_risk_metrics(self, data, metrics):
        """Calculate risk indicators"""
        occupied_data = data[~data['Is_Vacant']]
        
        # Tenant concentration
        tenant_revenue = occupied_data.groupby('Tenant_Name')['Annual_Rent'].sum().sort_values(ascending=False)
        total_revenue = tenant_revenue.sum()
        
        top_5_concentration = (tenant_revenue.head(5).sum() / total_revenue * 100) if total_revenue > 0 else 0
        top_10_concentration = (tenant_revenue.head(10).sum() / total_revenue * 100) if total_revenue > 0 else 0
        
        # Calculate risk score (0-100, higher is riskier)
        risk_score = 0
        
        # Occupancy risk (0-30 points)
        occupancy = metrics['Q2_2025']['occupancy_rate']
        if occupancy < 85:
            risk_score += 30
        elif occupancy < 90:
            risk_score += 20
        elif occupancy < 95:
            risk_score += 10
        
        # WALT risk (0-30 points)
        walt = metrics['Q2_2025']['walt']
        if walt < 24:
            risk_score += 30
        elif walt < 36:
            risk_score += 20
        elif walt < 48:
            risk_score += 10
        
        # Near-term expiry risk (0-20 points)
        near_term_pct = metrics['Q2_2025']['near_term_expiry_pct']
        if near_term_pct > 25:
            risk_score += 20
        elif near_term_pct > 15:
            risk_score += 10
        elif near_term_pct > 10:
            risk_score += 5
        
        # Concentration risk (0-20 points)
        if top_10_concentration > 30:
            risk_score += 20
        elif top_10_concentration > 20:
            risk_score += 10
        elif top_10_concentration > 15:
            risk_score += 5
        
        return {
            'overall_risk_score': risk_score,
            'risk_level': 'High' if risk_score >= 60 else 'Medium' if risk_score >= 30 else 'Low',
            'top_5_concentration': top_5_concentration,
            'top_10_concentration': top_10_concentration,
            'unique_tenants': occupied_data['Tenant_Name'].nunique()
        }
    
    def generate_insights(self, fund, metrics):
        """Generate automated insights for a fund"""
        insights = []
        
        # Occupancy insights
        occ_change = metrics['q2_summary']['occupancy_change']
        if occ_change < -2:
            insights.append({
                'type': 'warning',
                'category': 'Occupancy',
                'message': f'Occupancy declined {abs(occ_change):.1f}pp in Q2 2025',
                'recommendation': 'Implement aggressive leasing campaign with concessions'
            })
        elif occ_change > 2:
            insights.append({
                'type': 'success',
                'category': 'Occupancy',
                'message': f'Occupancy improved {occ_change:.1f}pp in Q2 2025',
                'recommendation': 'Maintain momentum with selective rent increases'
            })
        
        # Revenue insights
        rev_change = metrics['q2_summary']['revenue_change']
        if rev_change < -5:
            insights.append({
                'type': 'danger',
                'category': 'Revenue',
                'message': f'Revenue declined {abs(rev_change):.1f}% quarter-over-quarter',
                'recommendation': 'Focus on tenant retention and backfill vacant space'
            })
        elif rev_change > 5:
            insights.append({
                'type': 'success',
                'category': 'Revenue',
                'message': f'Revenue grew {rev_change:.1f}% in Q2 2025',
                'recommendation': 'Continue rent optimization strategy'
            })
        
        # WALT insights
        walt = metrics['Q2_2025']['walt']
        if walt < 36:
            insights.append({
                'type': 'warning',
                'category': 'Lease Term',
                'message': f'WALT is only {walt:.1f} months, below 3-year threshold',
                'recommendation': 'Prioritize long-term lease renewals with incentives'
            })
        
        # Risk insights
        risk_level = metrics['risk_metrics']['risk_level']
        if risk_level == 'High':
            insights.append({
                'type': 'danger',
                'category': 'Risk',
                'message': f'Portfolio risk level is {risk_level}',
                'recommendation': 'Immediate executive attention required'
            })
        
        return insights