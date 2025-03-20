#!/bin/bash

# Set up Kaggle credentials if not already done
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "Kaggle credentials not found. Please set them up first:"
    echo "1. Create a Kaggle account and get your API token from https://www.kaggle.com/settings"
    echo "2. Run: mkdir -p ~/.kaggle && echo '{\"username\":\"YOUR_USERNAME\",\"key\":\"YOUR_KEY\"}' > ~/.kaggle/kaggle.json"
    echo "3. Run: chmod 600 ~/.kaggle/kaggle.json"
    exit 1
fi

# Create data directory
mkdir -p data

# Download Elastic Logs dataset
echo "Downloading Elastic Logs dataset from Kaggle..."
kaggle datasets download -d elastic/logs -p data --unzip

# Check if download was successful
if [ ! -f data/logs.json ]; then
    echo "Failed to download dataset!"
    exit 1
fi

# Convert JSON to CSV using Python
echo "Converting JSON logs to CSV format..."
python - << EOF
import pandas as pd
import json
import os

# Load JSON log data
with open("data/logs.json", "r") as file:
    logs = json.load(file)

# Convert to Pandas DataFrame
df = pd.DataFrame(logs)

# Print dataset info
print(f"Dataset contains {len(df)} log entries with columns: {df.columns.tolist()}")
print("\nSample data:")
print(df.head(3))

# Save as CSV for easy processing
df.to_csv("data/kaggle_logs.csv", index=False)
print("\nSuccessfully converted to CSV: data/kaggle_logs.csv")
EOF

echo "Dataset preparation complete!"