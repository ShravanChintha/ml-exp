# CLIP Image Analysis App - Render Deployment Guide

This document explains how to deploy the CLIP Image Analysis app to Render.com's free tier.

## Deployment Steps

1. Create a Render account at https://render.com/ (you can sign up with GitHub)

2. From your Render dashboard, click "New" and select "Blueprint"

3. Connect your GitHub repository containing this code

4. Render will detect the `render.yaml` file and set up the service automatically

5. Wait for the build and deployment to complete (this may take 5-10 minutes for the first deployment)

6. Once deployed, you can access your app at the provided URL

## Environment Variables

The following environment variables are automatically set in the `render.yaml` file:

- `PYTHONHTTPSVERIFY=0`: Disables Python's SSL verification
- `HF_HUB_DISABLE_SSL_VERIFICATION=1`: Disables Hugging Face's SSL verification
- `PYTHONUNBUFFERED=1`: Enables real-time logging

## Important Notes

- The first request may be slow as the CLIP model needs to be downloaded (unless you've pre-cached it)
- Render's free tier has limited resources, so the model loading might take longer than on a local machine
- The free tier has a limit of 750 hours per month of service runtime
- The service will spin down after periods of inactivity and spin up when accessed again (causing initial latency)

## Monitoring

You can monitor the service status and logs directly from your Render dashboard.
