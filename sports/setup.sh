#!/bin/bash

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# Create and activate conda environment
echo "Creating conda environment..."
conda env create -f environment.yml

# Activate environment
echo "Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate cricket-rag

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    read -p "Enter your Google API key: " api_key
    echo "GOOGLE_API_KEY=$api_key" > .env
    echo ".env file created successfully!"
else
    echo ".env file already exists."
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

echo "Setup complete! You can now run the application with:"
echo "streamlit run src/app.py"
