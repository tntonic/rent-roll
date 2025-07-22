import json
import pandas as pd
import numpy as np
from dashboard_data_processor import RentRollProcessor

# Function to convert metrics to serializable format
def convert_to_serializable(obj):
    """Convert numpy/pandas types to native Python types"""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

# Initialize processor and load data
print("Loading data...")
processor = RentRollProcessor()
processor.load_data()

# Calculate metrics for both funds
print("Calculating Fund 2 metrics...")
fund2_metrics = processor.calculate_fund_metrics('Fund 2')
print("Calculating Fund 3 metrics...")
fund3_metrics = processor.calculate_fund_metrics('Fund 3')

# Generate insights
print("Generating insights...")
fund2_insights = processor.generate_insights('Fund 2', fund2_metrics)
fund3_insights = processor.generate_insights('Fund 3', fund3_metrics)

# Prepare data for export
export_data = {
    'fund2': {
        'metrics': convert_to_serializable({
            'Q4_2024': fund2_metrics['Q4_2024'],
            'Q1_2025': fund2_metrics['Q1_2025'],
            'Q2_2025': fund2_metrics['Q2_2025'],
            'q2_summary': fund2_metrics['q2_summary'],
            'top_properties': fund2_metrics['top_properties'],
            'expiry_analysis': fund2_metrics['expiry_analysis'],
            'risk_metrics': fund2_metrics['risk_metrics']
        }),
        'insights': convert_to_serializable(fund2_insights)
    },
    'fund3': {
        'metrics': convert_to_serializable({
            'Q4_2024': fund3_metrics['Q4_2024'],
            'Q1_2025': fund3_metrics['Q1_2025'],
            'Q2_2025': fund3_metrics['Q2_2025'],
            'q2_summary': fund3_metrics['q2_summary'],
            'top_properties': fund3_metrics['top_properties'],
            'expiry_analysis': fund3_metrics['expiry_analysis'],
            'risk_metrics': fund3_metrics['risk_metrics']
        }),
        'insights': convert_to_serializable(fund3_insights)
    },
    'metadata': {
        'generated_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': 'Q2 2025',
        'source_files': [
            'Faropoint Rent Roll All Funds (24DEC).xlsx',
            'Faropoint Rent Roll All Funds (25MAR).xlsx',
            'Faropoint Rent Roll All Funds (25JUN).xlsx'
        ]
    }
}

# Save to JSON file
print("Exporting data to JSON...")
with open('docs/data/dashboard_data.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print("Data exported successfully to docs/data/dashboard_data.json")