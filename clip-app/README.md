# Image Analysis with CLIP

This is a simple Streamlit application that uses OpenAI's CLIP (Contrastive Language-Image Pre-training) model to analyze the content of uploaded images.

## Features

- Upload images (JPG, JPEG, PNG)
- Get analysis of what's in the image using CLIP model
- Display confidence levels for different categories
- Option to download and use the model locally to avoid SSL issues

## Running Locally

1. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   - Standard version:
     ```
     streamlit run app.py
     ```
   - Version with local model support (recommended if you have SSL issues):
     ```
     streamlit run app_local.py
     ```

3. If you encounter SSL certificate issues, you can pre-download the model:
   ```
   python download_model.py
   ```

## Deployment Options

### Docker Deployment
```
docker-compose up -d
```

### Render.com (Free)
See [RENDER-DEPLOYMENT.md](RENDER-DEPLOYMENT.md) for detailed instructions, or run:
```
./deploy-to-render.sh
```

### Heroku (Free Tier)
```
heroku create
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Kubernetes
See [KUBERNETES-GUIDE.md](KUBERNETES-GUIDE.md) for detailed instructions on deploying with Kubernetes.

## Docker Deployment

### Using Docker Compose (Recommended)

1. Build and start the container:
   ```
   docker-compose up -d
   ```

2. Access the application at http://localhost:8501

3. To stop the application:
   ```
   docker-compose down
   ```

### Using Docker Directly

1. Build the Docker image:
   ```
   docker build -t image-analyzer .
   ```

2. Run the container:
   ```
   docker run -p 8501:8501 image-analyzer
   ```

3. Access the application at http://localhost:8501

## Troubleshooting SSL Certificate Issues

If you encounter SSL certificate verification errors when loading the model, try the following solutions:

1. **Use the Local Model Version**: Run `streamlit run app_local.py` which includes a button to download the model locally.

2. **Pre-download the Model**: Run `python download_model.py` to download the model files before starting the app.

3. **Update Certificates**: Make sure your system's CA certificates are up to date.

4. **Docker Deployment with SSL Fix**: The Docker setup has been enhanced to handle SSL certificate issues:
   - Includes proper certificate installation
   - Uses fallback model if download fails
   - Sets proper environment variables for SSL
   - Provides an entrypoint script that refreshes certificates

5. **macOS Certificate Helper**: For macOS users, run the included helper script:
   ```
   ./fix_ssl_macos.sh
   ```
   This will configure SSL certificates properly for macOS.

6. **Manual SSL Fix**: Set these environment variables before running the app:
   ```
   export PYTHONHTTPSVERIFY=0
   export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt  # Linux
   export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt  # Linux
   # For macOS:
   # export REQUESTS_CA_BUNDLE=/etc/ssl/cert.pem
   # export SSL_CERT_FILE=/etc/ssl/cert.pem
   ```

## How It Works

The application uses the CLIP model from the Hugging Face Transformers library. CLIP (Contrastive Language-Image Pre-training) was trained on a variety of image-text pairs and can understand both images and text.

When you upload an image, the model compares it against a set of predefined categories and returns confidence scores for each category.

## Requirements

See requirements.txt for the full list of dependencies.
