#!/bin/bash

# AGAE-Layzer V2.0 Installation Script
# This script installs all required dependencies

echo "================================================================================"
echo "AGAE-LAYZER V2.0 - Installation Script"
echo "================================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo ""
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "Installation completed successfully!"
    echo "================================================================================"
    echo ""
    echo "To start the application, run:"
    echo "  python3 run.py"
    echo ""
    echo "Then open your browser and navigate to:"
    echo "  http://localhost:5000"
    echo ""
    echo "For more information, see README.md and USAGE_GUIDE.md"
    echo "================================================================================"
else
    echo ""
    echo "Error: Installation failed. Please check the error messages above."
    exit 1
fi

