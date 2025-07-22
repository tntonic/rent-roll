import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Read the Excel file, skipping the first 4 rows
df = pd.read_excel('Faropoint Rent Roll All Funds (25JUN).xlsx', sheet_name='Report1', skiprows=4)

# Clean column names
df.columns = ['Property', 'Units', 'Lease', 'Lease_Type', 'Area', 'Lease_From', 'Lease_To', 
              'Term', 'Tenancy_Years', 'Monthly_Rent', 'Monthly_Rent_Area', 'Annual_Rent', 
              'Annual_Rent_Area', 'Annual_Rec_Area', 'Annual_Misc_Area', 'Security_Deposit', 'LOC_Amount']

# Remove empty rows
df = df.dropna(subset=['Property'])

# Extract property code from Property column
df['Prop_Code'] = df['Property'].str.extract(r'\(([^)]+)\)')

# Identify Fund based on property code
df['Fund'] = df['Prop_Code'].apply(lambda x: 'Fund 3' if str(x).startswith('3') else ('Fund 2' if str(x).startswith('x') else 'Other') if pd.notna(x) else 'Unknown')

# Reference date
reference_date = datetime(2025, 6, 30)

# Convert Lease_To to datetime
df['Lease_To'] = pd.to_datetime(df['Lease_To'], errors='coerce')

# Identify vacant spaces
df['Is_Vacant'] = df['Lease'].str.contains('VACANT', na=False)

# Calculate months to expiration from reference date
df['Months_To_Expiry'] = df.apply(lambda row: 
    max((row['Lease_To'] - reference_date).days / 30.44, 0) if pd.notna(row['Lease_To']) and not row['Is_Vacant'] else 0, 
    axis=1)

# Convert Area to numeric
df['Area'] = pd.to_numeric(df['Area'], errors='coerce')

# Filter out rows without valid area
df_valid = df[df['Area'].notna() & (df['Area'] > 0)]

# Calculate WALT by Fund
def calculate_walt(data, fund_name, include_vacant=True):
    if include_vacant:
        fund_data = data[data['Fund'] == fund_name]
    else:
        fund_data = data[(data['Fund'] == fund_name) & (~data['Is_Vacant'])]
    
    if len(fund_data) == 0 or fund_data['Area'].sum() == 0:
        return 0
    
    # WALT = Sum(Area * Months_To_Expiry) / Sum(Area)
    walt = (fund_data['Area'] * fund_data['Months_To_Expiry']).sum() / fund_data['Area'].sum()
    return walt

# Calculate WALT for each fund
print('=' * 70)
print('WALT CALCULATION RESULTS (Weighted Average Lease Term)')
print('Reference Date: June 30, 2025')
print('=' * 70)

for fund in ['Fund 2', 'Fund 3']:
    fund_data = df_valid[df_valid['Fund'] == fund]
    
    # With vacant spaces
    walt_with_vacant = calculate_walt(df_valid, fund, include_vacant=True)
    total_sf_with_vacant = fund_data['Area'].sum()
    vacant_sf = fund_data[fund_data['Is_Vacant']]['Area'].sum()
    
    # Without vacant spaces
    walt_without_vacant = calculate_walt(df_valid, fund, include_vacant=False)
    occupied_data = fund_data[~fund_data['Is_Vacant']]
    total_sf_without_vacant = occupied_data['Area'].sum()
    
    fund_prefix = '3' if fund == 'Fund 3' else 'x'
    print(f'\n{fund} (Property codes starting with "{fund_prefix}"):')
    print(f'  Total Lease Records: {len(fund_data)}')
    print(f'  Vacant Spaces: {fund_data.Is_Vacant.sum()}')
    print(f'  Total SF: {total_sf_with_vacant:,.0f}')
    print(f'  Vacant SF: {vacant_sf:,.0f} ({vacant_sf/total_sf_with_vacant*100:.1f}%)')
    print(f'  Occupied SF: {total_sf_without_vacant:,.0f}')
    print(f'  \n  WALT (including vacant spaces): {walt_with_vacant:.1f} months')
    print(f'  WALT (excluding vacant spaces): {walt_without_vacant:.1f} months')

# Summary comparison
print('\n' + '=' * 70)
print('SUMMARY COMPARISON')
print('=' * 70)
print('\n{:<15} {:>20} {:>20}'.format('', 'With Vacant', 'Without Vacant'))
print('-' * 55)
for fund in ['Fund 2', 'Fund 3']:
    walt_with = calculate_walt(df_valid, fund, include_vacant=True)
    walt_without = calculate_walt(df_valid, fund, include_vacant=False)
    print(f'{fund:<15} {walt_with:>15.1f} months {walt_without:>15.1f} months')