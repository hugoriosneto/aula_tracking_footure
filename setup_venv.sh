#!/bin/bash
# Script to set up the virtual environment for football tracking visualization

# Exit on error
set -e

echo "Setting up virtual environment for Football Tracking Visualization..."

# Create virtual environment
python3.10 -m venv venv
echo "Virtual environment created in ./venv/"

# Activate the virtual environment
case "$(uname -s)" in
    Linux*|Darwin*)
        source venv/bin/activate
        ;;
    CYGWIN*|MINGW*|MSYS*)
        source venv/Scripts/activate
        ;;
    *)
        echo "Unsupported OS. Please activate the virtual environment manually:"
        echo "  On Windows: venv\\Scripts\\activate"
        echo "  On macOS/Linux: source venv/bin/activate"
        exit 1
        ;;
esac

echo "Virtual environment activated"

# Install requirements
pip install --upgrade pip
echo "Installing required packages..."
pip install -r requirements.txt

# Download sample data
echo "Downloading sample data..."
python download_sample_data.py


echo ""
echo "Setup completed successfully!"
echo ""
echo "To activate the virtual environment again later:"
echo "  On Windows: venv\\Scripts\\activate"
echo "  On macOS/Linux: source venv/bin/activate"
echo ""
echo "To run the notebooks:"
echo "jupyter notebook" 