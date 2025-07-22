import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

# Read the Excel file
df = pd.read_excel('Faropoint Rent Roll All Funds (25JUN).xlsx', sheet_name='Report1', skiprows=4)

# Clean column names
df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
              'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
              'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']

# Data cleaning and preparation
df = df.dropna(subset=['Property'])
df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')
df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')

# Reference date
reference_date = datetime(2025, 6, 30)

# Process dates and identify vacancies
df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')
df['Lease_From'] = pd.to_datetime(df['Lease_From'], errors='coerce')
df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)
df['Months_To_Expiry'] = df.apply(lambda row: 
    max((row['Lease_To'] - reference_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
    axis=1)

# Convert numeric columns
numeric_cols = ['Area', 'Monthly_Rent', 'Annual_Rent', 'Annual_Rent_Area', 'Security_Deposit', 'LOC_Amount']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Filter valid data
df_valid = df[df['Area'].notna() & (df['Area'] > 0) & df['Fund'].isin(['Fund 2', 'Fund 3'])]

# Extract tenant name from Lease column
df_valid['Tenant_Name'] = df_valid['Lease'].str.extract(r'^([^(]+)')
df_valid['Tenant_Name'] = df_valid['Tenant_Name'].str.strip()

print("=" * 80)
print("COMPREHENSIVE RENT ROLL ANALYSIS BY FUND")
print("Analysis Date: June 30, 2025")
print("=" * 80)

# 1. PORTFOLIO OVERVIEW
print("\n1. PORTFOLIO OVERVIEW")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    
    # Property count
    unique_properties = fund_data['Prop_Code'].nunique()
    total_leases = len(fund_data)
    vacant_leases = fund_data['Is_Vacant'].sum()
    occupied_leases = total_leases - vacant_leases
    
    # Square footage
    total_sf = fund_data['Area'].sum()
    vacant_sf = fund_data[fund_data['Is_Vacant']]['Area'].sum()
    occupied_sf = total_sf - vacant_sf
    
    # Revenue metrics
    occupied_data = fund_data[~fund_data['Is_Vacant']]
    annual_revenue = occupied_data['Annual_Rent'].sum()
    avg_rent_psf = annual_revenue / occupied_sf if occupied_sf > 0 else 0
    
    print(f"\n{fund}:")
    print(f"  Properties: {unique_properties}")
    print(f"  Total Leases: {total_leases} (Occupied: {occupied_leases}, Vacant: {vacant_leases})")
    print(f"  Total SF: {total_sf:,.0f}")
    print(f"  Occupied SF: {occupied_sf:,.0f} ({occupied_sf/total_sf*100:.1f}%)")
    print(f"  Vacant SF: {vacant_sf:,.0f} ({vacant_sf/total_sf*100:.1f}%)")
    print(f"  Annual Revenue: ${annual_revenue:,.0f}")
    print(f"  Average Rent/SF: ${avg_rent_psf:.2f}")

# 2. LEASE EXPIRATION RISK ANALYSIS
print("\n\n2. LEASE EXPIRATION RISK ANALYSIS")
print("-" * 50)

# Create expiration buckets
def categorize_expiration(months):
    if months == 0:
        return 'Expired/Vacant'
    elif months <= 6:
        return '0-6 months'
    elif months <= 12:
        return '6-12 months'
    elif months <= 24:
        return '12-24 months'
    elif months <= 36:
        return '24-36 months'
    elif months <= 60:
        return '36-60 months'
    else:
        return '60+ months'

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    fund_data['Expiry_Bucket'] = fund_data['Months_To_Expiry'].apply(categorize_expiration)
    
    # Group by expiration bucket
    expiry_summary = fund_data.groupby('Expiry_Bucket').agg({
        'Area': ['count', 'sum'],
        'Annual_Rent': 'sum'
    }).round(0)
    
    print(f"\n{fund} Lease Expiration Schedule:")
    print(f"{'Expiry Period':<20} {'Leases':>10} {'SF':>15} {'Annual Rent':>20} {'% of Rent':>10}")
    print("-" * 80)
    
    total_rent = fund_data[~fund_data['Is_Vacant']]['Annual_Rent'].sum()
    
    bucket_order = ['Expired/Vacant', '0-6 months', '6-12 months', '12-24 months', 
                    '24-36 months', '36-60 months', '60+ months']
    
    for bucket in bucket_order:
        if bucket in expiry_summary.index:
            row = expiry_summary.loc[bucket]
            lease_count = row[('Area', 'count')]
            sf = row[('Area', 'sum')]
            rent = row[('Annual_Rent', 'sum')]
            rent_pct = (rent / total_rent * 100) if total_rent > 0 else 0
            print(f"{bucket:<20} {int(lease_count):>10} {sf:>15,.0f} ${rent:>18,.0f} {rent_pct:>9.1f}%")

# 3. RENT ANALYSIS
print("\n\n3. RENT ANALYSIS BY FUND")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & (~df_valid['Is_Vacant'])]
    
    if len(fund_data) > 0:
        # Calculate rent statistics
        rent_stats = {
            'Mean Rent/SF': fund_data['Annual_Rent_Area'].mean(),
            'Median Rent/SF': fund_data['Annual_Rent_Area'].median(),
            'Min Rent/SF': fund_data['Annual_Rent_Area'].min(),
            'Max Rent/SF': fund_data['Annual_Rent_Area'].max(),
            'Std Dev': fund_data['Annual_Rent_Area'].std()
        }
        
        print(f"\n{fund} Rent Statistics (Annual Rent/SF):")
        for metric, value in rent_stats.items():
            print(f"  {metric}: ${value:.2f}")
        
        # Rent distribution by quartiles
        quartiles = fund_data['Annual_Rent_Area'].quantile([0.25, 0.5, 0.75])
        print(f"  25th Percentile: ${quartiles[0.25]:.2f}")
        print(f"  50th Percentile: ${quartiles[0.50]:.2f}")
        print(f"  75th Percentile: ${quartiles[0.75]:.2f}")

# 4. TENANT CONCENTRATION ANALYSIS
print("\n\n4. TENANT CONCENTRATION ANALYSIS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & (~df_valid['Is_Vacant'])]
    
    # Group by tenant
    tenant_summary = fund_data.groupby('Tenant_Name').agg({
        'Area': 'sum',
        'Annual_Rent': 'sum'
    }).sort_values('Annual_Rent', ascending=False)
    
    total_rent = tenant_summary['Annual_Rent'].sum()
    
    # Top 10 tenants
    print(f"\n{fund} - Top 10 Tenants by Annual Rent:")
    print(f"{'Tenant':<40} {'SF':>12} {'Annual Rent':>15} {'% of Rent':>10}")
    print("-" * 80)
    
    for i, (tenant, row) in enumerate(tenant_summary.head(10).iterrows()):
        rent_pct = (row['Annual_Rent'] / total_rent * 100) if total_rent > 0 else 0
        print(f"{tenant[:39]:<40} {row['Area']:>12,.0f} ${row['Annual_Rent']:>14,.0f} {rent_pct:>9.1f}%")
    
    # Concentration metrics
    top_5_pct = (tenant_summary.head(5)['Annual_Rent'].sum() / total_rent * 100) if total_rent > 0 else 0
    top_10_pct = (tenant_summary.head(10)['Annual_Rent'].sum() / total_rent * 100) if total_rent > 0 else 0
    
    print(f"\n  Concentration Metrics:")
    print(f"    Top 5 tenants: {top_5_pct:.1f}% of rent")
    print(f"    Top 10 tenants: {top_10_pct:.1f}% of rent")
    print(f"    Total unique tenants: {len(tenant_summary)}")

# 5. PROPERTY PERFORMANCE ANALYSIS
print("\n\n5. PROPERTY PERFORMANCE ANALYSIS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    
    # Group by property
    property_summary = fund_data.groupby(['Prop_Code', 'Property']).agg({
        'Area': 'sum',
        'Annual_Rent': 'sum',
        'Is_Vacant': 'sum'
    })
    
    # Calculate occupancy and avg rent per property
    property_summary['Occupancy_Rate'] = 1 - (property_summary['Is_Vacant'] > 0).astype(int)
    property_summary['Avg_Rent_PSF'] = property_summary['Annual_Rent'] / property_summary['Area']
    
    # Sort by annual rent
    property_summary = property_summary.sort_values('Annual_Rent', ascending=False)
    
    print(f"\n{fund} - Top 5 Properties by Annual Rent:")
    print(f"{'Property':<40} {'SF':>12} {'Annual Rent':>15} {'Avg $/SF':>10}")
    print("-" * 80)
    
    for i, (idx, row) in enumerate(property_summary.head(5).iterrows()):
        prop_name = idx[1].split('(')[0].strip()[:39]
        print(f"{prop_name:<40} {row['Area']:>12,.0f} ${row['Annual_Rent']:>14,.0f} ${row['Avg_Rent_PSF']:>9.2f}")

# 6. VACANCY ANALYSIS
print("\n\n6. VACANCY ANALYSIS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    
    # Vacancy by property
    vacancy_by_property = fund_data.groupby('Prop_Code').agg({
        'Area': 'sum',
        'Is_Vacant': lambda x: x.sum() > 0
    })
    
    vacant_properties = vacancy_by_property[vacancy_by_property['Is_Vacant']].index.tolist()
    
    # Vacant space details
    vacant_spaces = fund_data[fund_data['Is_Vacant']]
    
    print(f"\n{fund} Vacancy Analysis:")
    print(f"  Properties with vacancy: {len(vacant_properties)} out of {fund_data['Prop_Code'].nunique()}")
    print(f"  Total vacant spaces: {len(vacant_spaces)}")
    print(f"  Total vacant SF: {vacant_spaces['Area'].sum():,.0f}")
    
    # Estimate potential revenue
    avg_rent_psf = fund_data[~fund_data['Is_Vacant']]['Annual_Rent_Area'].mean()
    potential_revenue = vacant_spaces['Area'].sum() * avg_rent_psf
    
    print(f"  Potential annual revenue if leased: ${potential_revenue:,.0f}")
    print(f"  (Based on average rent of ${avg_rent_psf:.2f}/SF)")

# 7. FINANCIAL RISK INDICATORS
print("\n\n7. FINANCIAL RISK INDICATORS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & (~df_valid['Is_Vacant'])]
    
    # Security deposit coverage
    total_security = fund_data['Security_Deposit'].sum()
    total_loc = fund_data['LOC_Amount'].sum()
    total_monthly_rent = fund_data['Monthly_Rent'].sum()
    
    # Calculate coverage ratio
    security_coverage = (total_security + total_loc) / total_monthly_rent if total_monthly_rent > 0 else 0
    
    print(f"\n{fund} Security Analysis:")
    print(f"  Total Security Deposits: ${total_security:,.0f}")
    print(f"  Total LOC/Bank Guarantees: ${total_loc:,.0f}")
    print(f"  Total Monthly Rent: ${total_monthly_rent:,.0f}")
    print(f"  Security Coverage Ratio: {security_coverage:.2f} months")
    
    # Leases without security
    no_security = fund_data[(fund_data['Security_Deposit'] == 0) & (fund_data['LOC_Amount'] == 0)]
    print(f"  Leases without security: {len(no_security)} ({len(no_security)/len(fund_data)*100:.1f}%)")

# 8. KEY INSIGHTS SUMMARY
print("\n\n8. KEY INSIGHTS AND RECOMMENDATIONS")
print("=" * 80)

print("\nFUND COMPARISON:")
print("-" * 50)

# Calculate key metrics for comparison
comparison_metrics = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    occupied_data = fund_data[~fund_data['Is_Vacant']]
    
    metrics = {
        'Fund': fund,
        'Occupancy': (1 - fund_data['Is_Vacant'].sum() / len(fund_data)) * 100,
        'WALT': (occupied_data['Area'] * occupied_data['Months_To_Expiry']).sum() / occupied_data['Area'].sum(),
        'Avg Rent PSF': occupied_data['Annual_Rent'].sum() / occupied_data['Area'].sum(),
        'Near-term Risk': occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum() / occupied_data['Area'].sum() * 100
    }
    comparison_metrics.append(metrics)

comparison_df = pd.DataFrame(comparison_metrics)
print(comparison_df.to_string(index=False))

print("\n\nKEY INSIGHTS:")
print("-" * 50)

# Generate insights based on analysis
insights = []

# Occupancy insights
if comparison_df.iloc[0]['Occupancy'] < comparison_df.iloc[1]['Occupancy']:
    insights.append(f"• Fund 3 has stronger occupancy ({comparison_df.iloc[1]['Occupancy']:.1f}%) vs Fund 2 ({comparison_df.iloc[0]['Occupancy']:.1f}%)")
else:
    insights.append(f"• Fund 2 has stronger occupancy ({comparison_df.iloc[0]['Occupancy']:.1f}%) vs Fund 3 ({comparison_df.iloc[1]['Occupancy']:.1f}%)")

# WALT insights
insights.append(f"• Fund 3 has longer WALT ({comparison_df.iloc[1]['WALT']:.1f} months) indicating more stable income")
insights.append(f"• Fund 2 faces higher near-term lease rollover risk ({comparison_df.iloc[0]['Near-term Risk']:.1f}% expiring within 12 months)")

# Rent insights
if comparison_df.iloc[0]['Avg Rent PSF'] > comparison_df.iloc[1]['Avg Rent PSF']:
    insights.append(f"• Fund 2 achieves higher average rents (${comparison_df.iloc[0]['Avg Rent PSF']:.2f}/SF) vs Fund 3 (${comparison_df.iloc[1]['Avg Rent PSF']:.2f}/SF)")
else:
    insights.append(f"• Fund 3 achieves higher average rents (${comparison_df.iloc[1]['Avg Rent PSF']:.2f}/SF) vs Fund 2 (${comparison_df.iloc[0]['Avg Rent PSF']:.2f}/SF)")

for insight in insights:
    print(insight)

print("\n\nRECOMMENDATIONS:")
print("-" * 50)
print("• Focus leasing efforts on Fund 2 properties given higher vacancy rate")
print("• Proactively engage tenants with leases expiring in next 12 months")
print("• Consider rent growth opportunities for below-market leases")
print("• Evaluate tenant concentration risk and diversification strategies")
print("• Review security deposit requirements for high-value tenants")