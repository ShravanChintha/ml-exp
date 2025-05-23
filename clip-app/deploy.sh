#!/bin/bash
# deploy.sh - Deployment script for CLIP Image Analysis App to Render.com

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Render CLI not found. Installing..."
    pip install render
fi

# Authenticate with Render (if needed)
if ! render whoami &> /dev/null; then
    echo "Please log in to Render:"
    render login
fi

# Deploy to Render
echo "Deploying CLIP Image Analysis App to Render..."
render deploy

echo "Deployment initiated. Check status in the Render dashboard."
echo "Your app will be available at: https://clip-image-analysis.onrender.com"
