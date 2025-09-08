#!/bin/bash

# AI Patent Analyst - Streamlit App Startup Script
echo "🔬 Starting AI Patent Analyst..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please copy .env.example to .env and configure your settings."
    echo "📋 Required variables: GOOGLE_CLOUD_PROJECT_ID, BQ_DATASET_ID"
    exit 1
fi

# Load environment variables
source .env

# Check for required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT_ID not set in .env file"
    exit 1
fi

if [ -z "$BQ_DATASET_ID" ]; then
    echo "❌ Error: BQ_DATASET_ID not set in .env file"
    exit 1
fi

echo "✅ Environment configured"
echo "📊 Project: $GOOGLE_CLOUD_PROJECT_ID"
echo "🗄️  Dataset: $BQ_DATASET_ID"

# Start Streamlit app directly on dashboard
echo "🚀 Starting Patent Intelligence Dashboard on http://localhost:8501"
python -m streamlit run app/main.py --server.address=0.0.0.0 --server.port=8501
