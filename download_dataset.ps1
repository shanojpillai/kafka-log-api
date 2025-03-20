# Create data directory
New-Item -ItemType Directory -Force -Path data

# Check for Kaggle credentials
if (-not (Test-Path "$env:USERPROFILE\.kaggle\kaggle.json")) {
    Write-Host "Kaggle credentials not found. Please set them up first:"
    Write-Host "1. Create a Kaggle account and get your API token from https://www.kaggle.com/settings"
    Write-Host "2. Create directory: mkdir -Force $env:USERPROFILE\.kaggle"
    Write-Host "3. Create credentials file with your details: `n   Set-Content -Path '$env:USERPROFILE\.kaggle\kaggle.json' -Value '{`"username`":`"YOUR_USERNAME`",`"key`":`"YOUR_KEY`"}`'"
    exit 1
}

# Download Elastic Logs dataset
Write-Host "Downloading Elastic Logs dataset from Kaggle..."
pip install kaggle
kaggle datasets download -d elastic/logs -p data --unzip

# Check if download was successful
if (-not (Test-Path "data\logs.json")) {
    Write-Host "Failed to download dataset!"
    exit 1
}

# Convert JSON to CSV using Python
Write-Host "Converting JSON logs to CSV format..."
python -c "
import pandas as pd
import json
import os

# Load JSON log data
with open('data/logs.json', 'r') as file:
    logs = json.load(file)

# Convert to Pandas DataFrame
df = pd.DataFrame(logs)

# Print dataset info
print(f'Dataset contains {len(df)} log entries with columns: {df.columns.tolist()}')
print('\nSample data:')
print(df.head(3))

# Save as CSV for easy processing
df.to_csv('data/kaggle_logs.csv', index=False)
print('\nSuccessfully converted to CSV: data/kaggle_logs.csv')
"

Write-Host "Dataset preparation complete!"