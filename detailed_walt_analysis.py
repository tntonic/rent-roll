import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Read the Excel file
df = pd.read_excel('Faropoint Rent Roll All Funds (25JUN).xlsx', sheet_name='Report1', skiprows=4)

# Clean column names
df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
              'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
              'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']

# Clean data
df = df.dropna(subset=['Property'])
df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')
df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')

# Reference date
reference_date = datetime(2025, 6, 30)

# Process dates and identify vacancies
df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')
df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)
df['Months_To_Expiry'] = df.apply(lambda row: 
    max((row['Lease_To'] - reference_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
    axis=1)

# Convert Area to numeric
df['Area'] = pd.to_numeric(df['Area'], errors='coerce')
df_valid = df[df['Area'].notna() & (df['Area'] > 0)]

# Additional analysis
print('\n' + '=' * 70)
print('LEASE EXPIRATION ANALYSIS BY FUND')
print('=' * 70)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    occupied_data = fund_data[~fund_data['Is_Vacant']]
    
    # Categorize by expiration periods
    expired = occupied_data[occupied_data['Lease_To'] < reference_date]
    exp_0_12 = occupied_data[(occupied_data['Lease_To'] >= reference_date) & 
                             (occupied_data['Months_To_Expiry'] <= 12)]
    exp_12_24 = occupied_data[(occupied_data['Months_To_Expiry'] > 12) & 
                              (occupied_data['Months_To_Expiry'] <= 24)]
    exp_24_36 = occupied_data[(occupied_data['Months_To_Expiry'] > 24) & 
                              (occupied_data['Months_To_Expiry'] <= 36)]
    exp_36_plus = occupied_data[occupied_data['Months_To_Expiry'] > 36]
    
    print(f'\n{fund} Lease Expiration Schedule:')
    print(f'  Already Expired:      {len(expired):>4} leases ({expired["Area"].sum():>10,.0f} SF) - {expired["Area"].sum()/occupied_data["Area"].sum()*100:>5.1f}%')
    print(f'  0-12 months:          {len(exp_0_12):>4} leases ({exp_0_12["Area"].sum():>10,.0f} SF) - {exp_0_12["Area"].sum()/occupied_data["Area"].sum()*100:>5.1f}%')
    print(f'  12-24 months:         {len(exp_12_24):>4} leases ({exp_12_24["Area"].sum():>10,.0f} SF) - {exp_12_24["Area"].sum()/occupied_data["Area"].sum()*100:>5.1f}%')
    print(f'  24-36 months:         {len(exp_24_36):>4} leases ({exp_24_36["Area"].sum():>10,.0f} SF) - {exp_24_36["Area"].sum()/occupied_data["Area"].sum()*100:>5.1f}%')
    print(f'  36+ months:           {len(exp_36_plus):>4} leases ({exp_36_plus["Area"].sum():>10,.0f} SF) - {exp_36_plus["Area"].sum()/occupied_data["Area"].sum()*100:>5.1f}%')

# Top 10 largest upcoming expirations
print('\n' + '=' * 70)
print('TOP 10 LARGEST UPCOMING LEASE EXPIRATIONS (Next 24 Months)')
print('=' * 70)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[(df_valid['Fund'] == fund) & 
                        (~df_valid['Is_Vacant']) & 
                        (df_valid['Months_To_Expiry'] > 0) & 
                        (df_valid['Months_To_Expiry'] <= 24)]
    fund_data = fund_data.sort_values('Area', ascending=False)
    
    if len(fund_data) > 0:
        print(f'\n{fund}:')
        top_10 = fund_data.head(10)
        for idx, row in top_10.iterrows():
            prop_name = row['Property'].split('(')[0].strip()
            print(f'  {prop_name[:40]:<40} {row["Area"]:>8,.0f} SF   Exp: {row["Lease_To"].strftime("%b %Y") if pd.notna(row["Lease_To"]) else "N/A":<10} ({row["Months_To_Expiry"]:.1f} months)')