# CLIP Image Analysis App - Heroku Deployment Guide

This document explains how to deploy the CLIP Image Analysis app to Heroku's free tier.

## Prerequisites

1. Create a Heroku account at https://signup.heroku.com/
2. Install the Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli

## Deployment Steps

1. Log in to Heroku via the CLI:
   ```
   heroku login
   ```

2. Create a new Heroku app:
   ```
   heroku create my-clip-image-app
   ```

3. Add a git remote for Heroku:
   ```
   heroku git:remote -a my-clip-image-app
   ```

4. Push your code to Heroku:
   ```
   git push heroku main
   ```

5. Scale the web dyno to start your app:
   ```
   heroku ps:scale web=1
   ```

6. Open your app in a browser:
   ```
   heroku open
   ```

## Environment Variables

The following environment variables are automatically set in the `app.json` file:

- `PYTHONHTTPSVERIFY=0`: Disables Python's SSL verification
- `HF_HUB_DISABLE_SSL_VERIFICATION=1`: Disables Hugging Face's SSL verification
- `PYTHONUNBUFFERED=1`: Enables real-time logging

## Important Notes

- The first request may be slow as the CLIP model needs to be downloaded
- Heroku's free tier has limited resources (512MB RAM, which may be too small for the CLIP model)
- The free tier has a limit of 550-1000 hours per month of dyno runtime
- The service will sleep after 30 minutes of inactivity on the free tier
- If memory issues occur, consider upgrading to a paid tier on Heroku

## Troubleshooting

View logs to debug issues:
```
heroku logs --tail
```
