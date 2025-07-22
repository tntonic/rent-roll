import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Function to process each rent roll file
def process_rent_roll(file_path, analysis_date):
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name='Report1', skiprows=4)
    
    # Clean column names
    df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
                  'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
                  'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']
    
    # Data cleaning
    df = df.dropna(subset=['Property'])
    df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')
    df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')
    
    # Process dates and identify vacancies
    df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')
    df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)
    df['Months_To_Expiry'] = df.apply(lambda row: 
        max((row['Lease_To'] - analysis_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
        axis=1)
    
    # Convert numeric columns
    numeric_cols = ['Area', 'Monthly_Rent', 'Annual_Rent', 'Annual_Rent_Area']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter valid data
    df_valid = df[df['Area'].notna() & (df['Area'] > 0) & df['Fund'].isin(['Fund 2', 'Fund 3'])]
    
    return df_valid

# Load all three files
print("Loading rent roll files...")
dec_data = process_rent_roll('Faropoint Rent Roll All Funds (24DEC).xlsx', datetime(2024, 12, 31))
mar_data = process_rent_roll('Faropoint Rent Roll All Funds (25MAR).xlsx', datetime(2025, 3, 31))
jun_data = process_rent_roll('Faropoint Rent Roll All Funds (25JUN).xlsx', datetime(2025, 6, 30))

print("Files loaded successfully!")

# Calculate metrics for each period
def calculate_metrics(data, period_name):
    metrics = {}
    
    for fund in ['Fund 2', 'Fund 3']:
        fund_data = data[data['Fund'] == fund]
        occupied_data = fund_data[~fund_data['Is_Vacant']]
        
        # Calculate WALT
        if len(occupied_data) > 0 and occupied_data['Area'].sum() > 0:
            walt = (occupied_data['Area'] * occupied_data['Months_To_Expiry']).sum() / occupied_data['Area'].sum()
        else:
            walt = 0
        
        metrics[fund] = {
            'Period': period_name,
            'Properties': fund_data['Prop_Code'].nunique(),
            'Total_Leases': len(fund_data),
            'Occupied_Leases': len(occupied_data),
            'Vacant_Leases': fund_data['Is_Vacant'].sum(),
            'Total_SF': fund_data['Area'].sum(),
            'Occupied_SF': occupied_data['Area'].sum(),
            'Vacant_SF': fund_data[fund_data['Is_Vacant']]['Area'].sum(),
            'Occupancy_Rate': (occupied_data['Area'].sum() / fund_data['Area'].sum() * 100) if fund_data['Area'].sum() > 0 else 0,
            'Annual_Revenue': occupied_data['Annual_Rent'].sum(),
            'Avg_Rent_PSF': occupied_data['Annual_Rent'].sum() / occupied_data['Area'].sum() if occupied_data['Area'].sum() > 0 else 0,
            'WALT': walt,
            'Near_Term_Expiry_SF': occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum(),
            'Near_Term_Expiry_Pct': (occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum() / 
                                     occupied_data['Area'].sum() * 100) if occupied_data['Area'].sum() > 0 else 0
        }
    
    return metrics

# Calculate metrics for all periods
dec_metrics = calculate_metrics(dec_data, 'Dec 2024')
mar_metrics = calculate_metrics(mar_data, 'Mar 2025')
jun_metrics = calculate_metrics(jun_data, 'Jun 2025')

# Print trend analysis
print("\n" + "=" * 80)
print("RENT ROLL TREND ANALYSIS - 6 MONTH OVERVIEW")
print("December 2024 → March 2025 → June 2025")
print("=" * 80)

# 1. PORTFOLIO SIZE TRENDS
print("\n1. PORTFOLIO SIZE TRENDS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    print(f"  Total SF:")
    print(f"    Dec 2024: {dec_metrics[fund]['Total_SF']:>15,.0f}")
    print(f"    Mar 2025: {mar_metrics[fund]['Total_SF']:>15,.0f}")
    print(f"    Jun 2025: {jun_metrics[fund]['Total_SF']:>15,.0f}")
    
    dec_to_jun_change = ((jun_metrics[fund]['Total_SF'] - dec_metrics[fund]['Total_SF']) / 
                         dec_metrics[fund]['Total_SF'] * 100) if dec_metrics[fund]['Total_SF'] > 0 else 0
    print(f"    6-Month Change: {dec_to_jun_change:>10.1f}%")

# 2. OCCUPANCY TRENDS
print("\n\n2. OCCUPANCY RATE TRENDS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    print(f"  Occupancy Rate:")
    print(f"    Dec 2024: {dec_metrics[fund]['Occupancy_Rate']:>10.1f}%")
    print(f"    Mar 2025: {mar_metrics[fund]['Occupancy_Rate']:>10.1f}%")
    print(f"    Jun 2025: {jun_metrics[fund]['Occupancy_Rate']:>10.1f}%")
    
    occ_change = jun_metrics[fund]['Occupancy_Rate'] - dec_metrics[fund]['Occupancy_Rate']
    print(f"    6-Month Change: {occ_change:>7.1f} pp")
    
    print(f"  Vacant SF:")
    print(f"    Dec 2024: {dec_metrics[fund]['Vacant_SF']:>15,.0f}")
    print(f"    Mar 2025: {mar_metrics[fund]['Vacant_SF']:>15,.0f}")
    print(f"    Jun 2025: {jun_metrics[fund]['Vacant_SF']:>15,.0f}")

# 3. REVENUE TRENDS
print("\n\n3. REVENUE TRENDS")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    print(f"  Annual Revenue:")
    print(f"    Dec 2024: ${dec_metrics[fund]['Annual_Revenue']:>14,.0f}")
    print(f"    Mar 2025: ${mar_metrics[fund]['Annual_Revenue']:>14,.0f}")
    print(f"    Jun 2025: ${jun_metrics[fund]['Annual_Revenue']:>14,.0f}")
    
    rev_change = ((jun_metrics[fund]['Annual_Revenue'] - dec_metrics[fund]['Annual_Revenue']) / 
                  dec_metrics[fund]['Annual_Revenue'] * 100) if dec_metrics[fund]['Annual_Revenue'] > 0 else 0
    print(f"    6-Month Growth: {rev_change:>8.1f}%")
    
    print(f"  Average Rent/SF:")
    print(f"    Dec 2024: ${dec_metrics[fund]['Avg_Rent_PSF']:>9.2f}")
    print(f"    Mar 2025: ${mar_metrics[fund]['Avg_Rent_PSF']:>9.2f}")
    print(f"    Jun 2025: ${jun_metrics[fund]['Avg_Rent_PSF']:>9.2f}")

# 4. WALT TRENDS
print("\n\n4. WALT TRENDS (Weighted Average Lease Term)")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    print(f"  WALT (months):")
    print(f"    Dec 2024: {dec_metrics[fund]['WALT']:>10.1f}")
    print(f"    Mar 2025: {mar_metrics[fund]['WALT']:>10.1f}")
    print(f"    Jun 2025: {jun_metrics[fund]['WALT']:>10.1f}")
    
    walt_change = jun_metrics[fund]['WALT'] - dec_metrics[fund]['WALT']
    print(f"    6-Month Change: {walt_change:>7.1f} months")

# 5. LEASE ROLLOVER RISK TRENDS
print("\n\n5. NEAR-TERM LEASE EXPIRY TRENDS (Next 12 Months)")
print("-" * 50)

for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    print(f"  SF Expiring in Next 12 Months:")
    print(f"    Dec 2024: {dec_metrics[fund]['Near_Term_Expiry_SF']:>15,.0f} ({dec_metrics[fund]['Near_Term_Expiry_Pct']:.1f}%)")
    print(f"    Mar 2025: {mar_metrics[fund]['Near_Term_Expiry_SF']:>15,.0f} ({mar_metrics[fund]['Near_Term_Expiry_Pct']:.1f}%)")
    print(f"    Jun 2025: {jun_metrics[fund]['Near_Term_Expiry_SF']:>15,.0f} ({jun_metrics[fund]['Near_Term_Expiry_Pct']:.1f}%)")

# 6. LEASING ACTIVITY ANALYSIS
print("\n\n6. LEASING ACTIVITY ANALYSIS")
print("-" * 50)

# Identify new leases and expirations
for fund in ['Fund 2', 'Fund 3']:
    print(f"\n{fund}:")
    
    # Count leases by tenant name to track changes
    dec_tenants = set(dec_data[(dec_data['Fund'] == fund) & (~dec_data['Is_Vacant'])]['Lease'].unique())
    mar_tenants = set(mar_data[(mar_data['Fund'] == fund) & (~mar_data['Is_Vacant'])]['Lease'].unique())
    jun_tenants = set(jun_data[(jun_data['Fund'] == fund) & (~jun_data['Is_Vacant'])]['Lease'].unique())
    
    new_in_mar = len(mar_tenants - dec_tenants)
    lost_by_mar = len(dec_tenants - mar_tenants)
    new_in_jun = len(jun_tenants - mar_tenants)
    lost_by_jun = len(mar_tenants - jun_tenants)
    
    print(f"  Dec 2024 → Mar 2025:")
    print(f"    New Leases: {new_in_mar}")
    print(f"    Lost Leases: {lost_by_mar}")
    print(f"  Mar 2025 → Jun 2025:")
    print(f"    New Leases: {new_in_jun}")
    print(f"    Lost Leases: {lost_by_jun}")
    print(f"  Net Change (6 months): {len(jun_tenants) - len(dec_tenants)}")

# Create visualizations
print("\nCreating trend visualizations...")

# Set up the figure
fig = plt.figure(figsize=(20, 16))

# 1. Occupancy Trend
ax1 = plt.subplot(3, 3, 1)
periods = ['Dec 2024', 'Mar 2025', 'Jun 2025']
fund2_occ = [dec_metrics['Fund 2']['Occupancy_Rate'], mar_metrics['Fund 2']['Occupancy_Rate'], jun_metrics['Fund 2']['Occupancy_Rate']]
fund3_occ = [dec_metrics['Fund 3']['Occupancy_Rate'], mar_metrics['Fund 3']['Occupancy_Rate'], jun_metrics['Fund 3']['Occupancy_Rate']]

ax1.plot(periods, fund2_occ, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax1.plot(periods, fund3_occ, 's-', linewidth=2, markersize=8, label='Fund 3')
ax1.set_title('Occupancy Rate Trend', fontsize=14, fontweight='bold')
ax1.set_ylabel('Occupancy Rate (%)')
ax1.set_ylim(80, 95)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Revenue Trend
ax2 = plt.subplot(3, 3, 2)
fund2_rev = [dec_metrics['Fund 2']['Annual_Revenue']/1e6, mar_metrics['Fund 2']['Annual_Revenue']/1e6, jun_metrics['Fund 2']['Annual_Revenue']/1e6]
fund3_rev = [dec_metrics['Fund 3']['Annual_Revenue']/1e6, mar_metrics['Fund 3']['Annual_Revenue']/1e6, jun_metrics['Fund 3']['Annual_Revenue']/1e6]

ax2.plot(periods, fund2_rev, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax2.plot(periods, fund3_rev, 's-', linewidth=2, markersize=8, label='Fund 3')
ax2.set_title('Annual Revenue Trend', fontsize=14, fontweight='bold')
ax2.set_ylabel('Annual Revenue ($M)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. WALT Trend
ax3 = plt.subplot(3, 3, 3)
fund2_walt = [dec_metrics['Fund 2']['WALT'], mar_metrics['Fund 2']['WALT'], jun_metrics['Fund 2']['WALT']]
fund3_walt = [dec_metrics['Fund 3']['WALT'], mar_metrics['Fund 3']['WALT'], jun_metrics['Fund 3']['WALT']]

ax3.plot(periods, fund2_walt, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax3.plot(periods, fund3_walt, 's-', linewidth=2, markersize=8, label='Fund 3')
ax3.set_title('WALT Trend', fontsize=14, fontweight='bold')
ax3.set_ylabel('WALT (months)')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Vacant SF Trend
ax4 = plt.subplot(3, 3, 4)
fund2_vac = [dec_metrics['Fund 2']['Vacant_SF']/1e6, mar_metrics['Fund 2']['Vacant_SF']/1e6, jun_metrics['Fund 2']['Vacant_SF']/1e6]
fund3_vac = [dec_metrics['Fund 3']['Vacant_SF']/1e6, mar_metrics['Fund 3']['Vacant_SF']/1e6, jun_metrics['Fund 3']['Vacant_SF']/1e6]

ax4.plot(periods, fund2_vac, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax4.plot(periods, fund3_vac, 's-', linewidth=2, markersize=8, label='Fund 3')
ax4.set_title('Vacant Square Feet Trend', fontsize=14, fontweight='bold')
ax4.set_ylabel('Vacant SF (Millions)')
ax4.legend()
ax4.grid(True, alpha=0.3)

# 5. Average Rent PSF Trend
ax5 = plt.subplot(3, 3, 5)
fund2_rent = [dec_metrics['Fund 2']['Avg_Rent_PSF'], mar_metrics['Fund 2']['Avg_Rent_PSF'], jun_metrics['Fund 2']['Avg_Rent_PSF']]
fund3_rent = [dec_metrics['Fund 3']['Avg_Rent_PSF'], mar_metrics['Fund 3']['Avg_Rent_PSF'], jun_metrics['Fund 3']['Avg_Rent_PSF']]

ax5.plot(periods, fund2_rent, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax5.plot(periods, fund3_rent, 's-', linewidth=2, markersize=8, label='Fund 3')
ax5.set_title('Average Rent per SF Trend', fontsize=14, fontweight='bold')
ax5.set_ylabel('Average Rent ($/SF)')
ax5.legend()
ax5.grid(True, alpha=0.3)

# 6. Near-term Expiry Risk Trend
ax6 = plt.subplot(3, 3, 6)
fund2_risk = [dec_metrics['Fund 2']['Near_Term_Expiry_Pct'], mar_metrics['Fund 2']['Near_Term_Expiry_Pct'], jun_metrics['Fund 2']['Near_Term_Expiry_Pct']]
fund3_risk = [dec_metrics['Fund 3']['Near_Term_Expiry_Pct'], mar_metrics['Fund 3']['Near_Term_Expiry_Pct'], jun_metrics['Fund 3']['Near_Term_Expiry_Pct']]

ax6.plot(periods, fund2_risk, 'o-', linewidth=2, markersize=8, label='Fund 2')
ax6.plot(periods, fund3_risk, 's-', linewidth=2, markersize=8, label='Fund 3')
ax6.set_title('Near-term Expiry Risk Trend', fontsize=14, fontweight='bold')
ax6.set_ylabel('% of SF Expiring in 12 Months')
ax6.legend()
ax6.grid(True, alpha=0.3)

# 7. Portfolio Composition - Dec 2024
ax7 = plt.subplot(3, 3, 7)
labels = ['Fund 2', 'Fund 3']
sizes = [dec_metrics['Fund 2']['Total_SF'], dec_metrics['Fund 3']['Total_SF']]
ax7.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax7.set_title('Dec 2024 Portfolio (by SF)', fontsize=12, fontweight='bold')

# 8. Portfolio Composition - Mar 2025
ax8 = plt.subplot(3, 3, 8)
sizes = [mar_metrics['Fund 2']['Total_SF'], mar_metrics['Fund 3']['Total_SF']]
ax8.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax8.set_title('Mar 2025 Portfolio (by SF)', fontsize=12, fontweight='bold')

# 9. Portfolio Composition - Jun 2025
ax9 = plt.subplot(3, 3, 9)
sizes = [jun_metrics['Fund 2']['Total_SF'], jun_metrics['Fund 3']['Total_SF']]
ax9.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax9.set_title('Jun 2025 Portfolio (by SF)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('rent_roll_trend_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("Trend analysis visualizations saved to: rent_roll_trend_analysis.png")

# Key insights summary
print("\n" + "=" * 80)
print("KEY TREND INSIGHTS")
print("=" * 80)

print("\n🔍 PORTFOLIO EVOLUTION (Dec 2024 → Jun 2025):")
print("-" * 50)

# Calculate overall changes
for fund in ['Fund 2', 'Fund 3']:
    occ_change = jun_metrics[fund]['Occupancy_Rate'] - dec_metrics[fund]['Occupancy_Rate']
    rev_change = ((jun_metrics[fund]['Annual_Revenue'] - dec_metrics[fund]['Annual_Revenue']) / 
                  dec_metrics[fund]['Annual_Revenue'] * 100)
    walt_change = jun_metrics[fund]['WALT'] - dec_metrics[fund]['WALT']
    
    print(f"\n{fund}:")
    print(f"  • Occupancy: {'↑' if occ_change > 0 else '↓'} {abs(occ_change):.1f} pp")
    print(f"  • Revenue: {'↑' if rev_change > 0 else '↓'} {abs(rev_change):.1f}%")
    print(f"  • WALT: {'↑' if walt_change > 0 else '↓'} {abs(walt_change):.1f} months")
    print(f"  • Rent/SF: ${dec_metrics[fund]['Avg_Rent_PSF']:.2f} → ${jun_metrics[fund]['Avg_Rent_PSF']:.2f}")

print("\n📊 NOTABLE TRENDS:")
print("-" * 50)

# Identify key trends
trends = []

# Occupancy trends
if jun_metrics['Fund 2']['Occupancy_Rate'] < dec_metrics['Fund 2']['Occupancy_Rate']:
    trends.append("• Fund 2 occupancy declining - increased leasing focus needed")
if jun_metrics['Fund 3']['Occupancy_Rate'] > dec_metrics['Fund 3']['Occupancy_Rate']:
    trends.append("• Fund 3 showing positive occupancy momentum")

# WALT trends
if jun_metrics['Fund 2']['WALT'] < dec_metrics['Fund 2']['WALT'] - 3:
    trends.append("• Fund 2 WALT deteriorating - lease term structure weakening")
if jun_metrics['Fund 3']['WALT'] < dec_metrics['Fund 3']['WALT'] - 3:
    trends.append("• Fund 3 WALT declining - monitor lease rollover risk")

# Revenue trends
fund2_rev_growth = ((jun_metrics['Fund 2']['Annual_Revenue'] - dec_metrics['Fund 2']['Annual_Revenue']) / 
                    dec_metrics['Fund 2']['Annual_Revenue'] * 100)
fund3_rev_growth = ((jun_metrics['Fund 3']['Annual_Revenue'] - dec_metrics['Fund 3']['Annual_Revenue']) / 
                    dec_metrics['Fund 3']['Annual_Revenue'] * 100)

if fund2_rev_growth > 5:
    trends.append(f"• Fund 2 strong revenue growth: +{fund2_rev_growth:.1f}%")
elif fund2_rev_growth < -5:
    trends.append(f"• Fund 2 revenue declining: {fund2_rev_growth:.1f}%")

if fund3_rev_growth > 5:
    trends.append(f"• Fund 3 strong revenue growth: +{fund3_rev_growth:.1f}%")
elif fund3_rev_growth < -5:
    trends.append(f"• Fund 3 revenue declining: {fund3_rev_growth:.1f}%")

for trend in trends:
    print(trend)

print("\n⚠️  AREAS OF CONCERN:")
print("-" * 50)

concerns = []

# Check for increasing vacancy
if jun_metrics['Fund 2']['Vacant_SF'] > dec_metrics['Fund 2']['Vacant_SF'] * 1.1:
    concerns.append("• Fund 2 vacancy increasing significantly")
if jun_metrics['Fund 3']['Vacant_SF'] > dec_metrics['Fund 3']['Vacant_SF'] * 1.1:
    concerns.append("• Fund 3 vacancy increasing")

# Check for declining WALT
if jun_metrics['Fund 2']['WALT'] < 36:
    concerns.append("• Fund 2 WALT below 3 years - high rollover risk")
if jun_metrics['Fund 3']['WALT'] < 36:
    concerns.append("• Fund 3 WALT approaching critical levels")

# Near-term expiry risk
if jun_metrics['Fund 2']['Near_Term_Expiry_Pct'] > 20:
    concerns.append(f"• Fund 2: {jun_metrics['Fund 2']['Near_Term_Expiry_Pct']:.1f}% of space expiring within 12 months")
if jun_metrics['Fund 3']['Near_Term_Expiry_Pct'] > 20:
    concerns.append(f"• Fund 3: {jun_metrics['Fund 3']['Near_Term_Expiry_Pct']:.1f}% of space expiring within 12 months")

for concern in concerns:
    print(concern)

print("\n✅ POSITIVE DEVELOPMENTS:")
print("-" * 50)

positives = []

# Check for improvements
if jun_metrics['Fund 2']['Occupancy_Rate'] > dec_metrics['Fund 2']['Occupancy_Rate'] + 2:
    positives.append("• Fund 2 occupancy improving")
if jun_metrics['Fund 3']['Occupancy_Rate'] > dec_metrics['Fund 3']['Occupancy_Rate'] + 2:
    positives.append("• Fund 3 maintaining strong occupancy")

# Rent growth
if jun_metrics['Fund 2']['Avg_Rent_PSF'] > dec_metrics['Fund 2']['Avg_Rent_PSF'] * 1.02:
    positives.append(f"• Fund 2 achieving rent growth")
if jun_metrics['Fund 3']['Avg_Rent_PSF'] > dec_metrics['Fund 3']['Avg_Rent_PSF'] * 1.02:
    positives.append(f"• Fund 3 achieving rent growth")

for positive in positives:
    print(positive)

print("\n" + "=" * 80)