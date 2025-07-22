#!/bin/bash

echo "======================================"
echo "Q2 2025 BI Dashboard Launcher"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import dash" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

# Launch the dashboard
echo ""
echo "Launching Q2 2025 Performance Dashboard..."
echo "Dashboard will be available at: http://127.0.0.1:8050/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Run the dashboard
python3 q2_2025_bi_dashboard.py