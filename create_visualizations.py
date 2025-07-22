import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read and prepare data
df = pd.read_excel('Faropoint Rent Roll All Funds (25JUN).xlsx', sheet_name='Report1', skiprows=4)
df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
              'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
              'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']

# Data cleaning
df = df.dropna(subset=['Property'])
df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')
df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')

# Process dates and numeric columns
reference_date = datetime(2025, 6, 30)
df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')
df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)
df['Months_To_Expiry'] = df.apply(lambda row: 
    max((row['Lease_To'] - reference_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
    axis=1)

numeric_cols = ['Area', 'Monthly_Rent', 'Annual_Rent', 'Annual_Rent_Area']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_valid = df[df['Area'].notna() & (df['Area'] > 0) & df['Fund'].isin(['Fund 2', 'Fund 3'])]

# Create figure with subplots
fig = plt.figure(figsize=(20, 24))

# 1. Portfolio Composition Comparison
ax1 = plt.subplot(4, 2, 1)
portfolio_data = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    portfolio_data.append({
        'Fund': fund,
        'Occupied SF': fund_data[~fund_data['Is_Vacant']]['Area'].sum() / 1e6,
        'Vacant SF': fund_data[fund_data['Is_Vacant']]['Area'].sum() / 1e6
    })

portfolio_df = pd.DataFrame(portfolio_data)
portfolio_df.set_index('Fund').plot(kind='bar', stacked=True, ax=ax1)
ax1.set_title('Portfolio Composition by Fund (Million SF)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Square Feet (Millions)')
ax1.set_xlabel('')
ax1.legend(['Occupied', 'Vacant'])
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

# 2. Occupancy Rate Comparison
ax2 = plt.subplot(4, 2, 2)
occupancy_data = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    occ_rate = (1 - fund_data['Is_Vacant'].sum() / len(fund_data)) * 100
    occupancy_data.append({'Fund': fund, 'Occupancy %': occ_rate})

occ_df = pd.DataFrame(occupancy_data)
bars = ax2.bar(occ_df['Fund'], occ_df['Occupancy %'])
ax2.set_ylim(80, 95)
ax2.set_ylabel('Occupancy Rate (%)')
ax2.set_title('Occupancy Rate by Fund', fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars, occ_df['Occupancy %'])):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
             f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

# 3. WALT Comparison
ax3 = plt.subplot(4, 2, 3)
walt_data = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & (~df_valid['Is_Vacant'])]
    walt = (fund_data['Area'] * fund_data['Months_To_Expiry']).sum() / fund_data['Area'].sum()
    walt_data.append({'Fund': fund, 'WALT (months)': walt})

walt_df = pd.DataFrame(walt_data)
bars = ax3.bar(walt_df['Fund'], walt_df['WALT (months)'])
ax3.set_ylabel('WALT (months)')
ax3.set_title('Weighted Average Lease Term by Fund', fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars, walt_df['WALT (months)'])):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{val:.1f}', ha='center', va='bottom', fontweight='bold')

# 4. Average Rent PSF Comparison
ax4 = plt.subplot(4, 2, 4)
rent_data = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & (~df_valid['Is_Vacant'])]
    avg_rent = fund_data['Annual_Rent'].sum() / fund_data['Area'].sum()
    rent_data.append({'Fund': fund, 'Avg Rent $/SF': avg_rent})

rent_df = pd.DataFrame(rent_data)
bars = ax4.bar(rent_df['Fund'], rent_df['Avg Rent $/SF'])
ax4.set_ylabel('Average Rent ($/SF)')
ax4.set_title('Average Annual Rent per SF by Fund', fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars, rent_df['Avg Rent $/SF'])):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
             f'${val:.2f}', ha='center', va='bottom', fontweight='bold')

# 5. Lease Expiration Timeline - Fund 2
ax5 = plt.subplot(4, 2, 5)
fund2_data = df_valid[(df_valid['Fund'] == 'Fund 2') & (~df_valid['Is_Vacant'])]
expiry_buckets = ['0-6m', '6-12m', '12-24m', '24-36m', '36-60m', '60m+']
expiry_data = []

for bucket, (min_m, max_m) in zip(expiry_buckets, 
                                   [(0, 6), (6, 12), (12, 24), (24, 36), (36, 60), (60, 999)]):
    if max_m == 999:
        mask = fund2_data['Months_To_Expiry'] > min_m
    else:
        mask = (fund2_data['Months_To_Expiry'] > min_m) & (fund2_data['Months_To_Expiry'] <= max_m)
    
    sf = fund2_data[mask]['Area'].sum() / 1e6
    expiry_data.append(sf)

ax5.bar(expiry_buckets, expiry_data)
ax5.set_ylabel('Square Feet (Millions)')
ax5.set_title('Fund 2 - Lease Expiration Schedule', fontsize=14, fontweight='bold')
ax5.set_xlabel('Time to Expiration')

# 6. Lease Expiration Timeline - Fund 3
ax6 = plt.subplot(4, 2, 6)
fund3_data = df_valid[(df_valid['Fund'] == 'Fund 3') & (~df_valid['Is_Vacant'])]
expiry_data = []

for bucket, (min_m, max_m) in zip(expiry_buckets, 
                                   [(0, 6), (6, 12), (12, 24), (24, 36), (36, 60), (60, 999)]):
    if max_m == 999:
        mask = fund3_data['Months_To_Expiry'] > min_m
    else:
        mask = (fund3_data['Months_To_Expiry'] > min_m) & (fund3_data['Months_To_Expiry'] <= max_m)
    
    sf = fund3_data[mask]['Area'].sum() / 1e6
    expiry_data.append(sf)

ax6.bar(expiry_buckets, expiry_data)
ax6.set_ylabel('Square Feet (Millions)')
ax6.set_title('Fund 3 - Lease Expiration Schedule', fontsize=14, fontweight='bold')
ax6.set_xlabel('Time to Expiration')

# 7. Rent Distribution - Fund 2
ax7 = plt.subplot(4, 2, 7)
fund2_rents = fund2_data[fund2_data['Annual_Rent_Area'] > 0]['Annual_Rent_Area']
ax7.hist(fund2_rents, bins=30, edgecolor='black', alpha=0.7)
ax7.axvline(fund2_rents.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${fund2_rents.mean():.2f}')
ax7.axvline(fund2_rents.median(), color='green', linestyle='--', linewidth=2, label=f'Median: ${fund2_rents.median():.2f}')
ax7.set_xlabel('Annual Rent per SF ($)')
ax7.set_ylabel('Number of Leases')
ax7.set_title('Fund 2 - Rent Distribution', fontsize=14, fontweight='bold')
ax7.legend()
ax7.set_xlim(0, 25)

# 8. Rent Distribution - Fund 3
ax8 = plt.subplot(4, 2, 8)
fund3_rents = fund3_data[fund3_data['Annual_Rent_Area'] > 0]['Annual_Rent_Area']
ax8.hist(fund3_rents, bins=30, edgecolor='black', alpha=0.7)
ax8.axvline(fund3_rents.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${fund3_rents.mean():.2f}')
ax8.axvline(fund3_rents.median(), color='green', linestyle='--', linewidth=2, label=f'Median: ${fund3_rents.median():.2f}')
ax8.set_xlabel('Annual Rent per SF ($)')
ax8.set_ylabel('Number of Leases')
ax8.set_title('Fund 3 - Rent Distribution', fontsize=14, fontweight='bold')
ax8.legend()
ax8.set_xlim(0, 30)

plt.tight_layout()
plt.savefig('rent_roll_analysis_charts.png', dpi=300, bbox_inches='tight')
plt.close()

# Create a summary metrics table
fig2, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Prepare summary data
summary_data = []
for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    occupied_data = fund_data[~fund_data['Is_Vacant']]
    
    summary_data.append([
        fund,
        f"{fund_data['Prop_Code'].nunique()}",
        f"{fund_data['Area'].sum():,.0f}",
        f"{(1 - fund_data['Is_Vacant'].sum() / len(fund_data)) * 100:.1f}%",
        f"${occupied_data['Annual_Rent'].sum() / 1e6:.1f}M",
        f"${occupied_data['Annual_Rent'].sum() / occupied_data['Area'].sum():.2f}",
        f"{(occupied_data['Area'] * occupied_data['Months_To_Expiry']).sum() / occupied_data['Area'].sum():.1f}",
        f"{occupied_data[occupied_data['Months_To_Expiry'] <= 12]['Area'].sum() / occupied_data['Area'].sum() * 100:.1f}%"
    ])

# Create table
col_labels = ['Fund', 'Properties', 'Total SF', 'Occupancy', 'Annual Revenue', 'Avg Rent/SF', 'WALT (months)', 'Near-term Risk']
table = ax.table(cellText=summary_data, colLabels=col_labels, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)

# Style the table
for i in range(len(col_labels)):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(summary_data) + 1):
    for j in range(len(col_labels)):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#f0f0f0')

ax.set_title('Rent Roll Summary Metrics by Fund', fontsize=16, fontweight='bold', pad=20)
plt.savefig('rent_roll_summary_table.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations created successfully!")
print("Files saved:")
print("- rent_roll_analysis_charts.png")
print("- rent_roll_summary_table.png")