# CLIP Image Analysis App - Streamlit Cloud Deployment Guide

This document explains how to deploy the CLIP Image Analysis app to Streamlit Cloud's free tier.

## Prerequisites

1. Create a Streamlit Cloud account at https://streamlit.io/cloud (you can sign up with GitHub)
2. Push your code to a public GitHub repository

## Deployment Steps

1. Go to https://streamlit.io/cloud and log in with your GitHub account

2. Click "New app" and select your GitHub repository

3. Configure your app:
   - Repository: Select your GitHub repository
   - Branch: main (or your preferred branch)
   - Main file path: app.py
   - Advanced settings (optional):
     - Add the following environment variables:
       - PYTHONHTTPSVERIFY: 0
       - HF_HUB_DISABLE_SSL_VERIFICATION: 1
       - PYTHONUNBUFFERED: 1

4. Click "Deploy" and wait for the app to be deployed

5. Your app will be available at a URL like `https://username-repo-name-app-name.streamlit.app`

## Important Notes

- The first time the app runs, it will download the CLIP model which may take a few minutes
- Streamlit Cloud's free tier has generous resources for Streamlit apps
- The app will sleep after a period of inactivity
- The free tier has a limit on the number of hours per month (currently generous)

## Advantages of Streamlit Cloud

- Specifically designed for Streamlit apps
- Better resource allocation for machine learning models
- Simpler deployment process
- Native support for Streamlit's features

## Monitoring

You can monitor your app's status and logs directly from the Streamlit Cloud dashboard.
