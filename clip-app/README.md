# CLIP Image Analysis App - Render Kubernetes Deployment

A Streamlit application that uses OpenAI's CLIP model to analyze and classify images. This project is configured for seamless deployment to Render.com using Kubernetes with complete CI/CD capabilities.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Local Development](#local-development)
- [CI/CD Pipeline](#cicd-pipeline)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Project Overview

This application allows users to upload images, which are then analyzed using OpenAI's CLIP (Contrastive Language-Image Pre-Training) model. The model identifies objects, scenes, and other content within the uploaded images, providing confidence scores for each detection.

### Key Features

- **Image Upload and Analysis**: Upload images to be analyzed by the CLIP model
- **SSL Certificate Handling**: Built-in fixes for SSL certificate issues when fetching models
- **Prometheus Monitoring**: Track performance metrics like response time and error rates
- **Kubernetes Deployment**: Scalable infrastructure with auto-scaling capabilities
- **CI/CD Pipeline**: Automated testing, building, and deployment on code changes

### Tech Stack

- **Frontend & Backend**: Streamlit
- **ML Model**: OpenAI's CLIP (via Hugging Face Transformers)
- **Infrastructure**: Kubernetes on Render.com
- **Monitoring**: Prometheus with metrics exporter
- **CI/CD**: Render.com built-in CI/CD with GitHub integration

## Architecture

```
┌─────────────────┐     ┌───────────────────┐     ┌───────────────┐
│                 │     │                   │     │               │
│  User/Browser   │────▶│  Streamlit App    │────▶│  CLIP Model   │
│                 │     │                   │     │               │
└─────────────────┘     └───────────────────┘     └───────────────┘
                               │                         │
                               │                         │
                               ▼                         │
                        ┌──────────────┐                 │
                        │  Prometheus  │◀────────────────┘
                        │  Monitoring  │
                        └──────────────┘
```

### Components

1. **Streamlit App (`app.py`)**: The main application that handles user interactions, image uploads, and displays analysis results
2. **SSL Fix Module (`ssl_fix.py`)**: Handles SSL certificate issues when downloading models from Hugging Face
3. **Metrics Module (`metrics.py`)**: Collects and exposes performance metrics for Prometheus monitoring
4. **Kubernetes Config (`k8s.yaml`)**: Defines the Kubernetes resources for deployment
5. **Dockerfile**: Builds the container image for the application
6. **Render Config (`render.yaml`)**: Configures deployment to Render.com

## Local Development

### Prerequisites

- Python 3.10+
- Docker
- Git

### Setup and Installation

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd clip-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```bash
   streamlit run app.py
   ```

### Docker Development

Build and run the Docker container locally:

```bash
docker build -t clip-app:latest .
docker run -p 8501:8501 clip-app:latest
```

## CI/CD Pipeline

This project uses Render.com's built-in CI/CD capabilities with Kubernetes integration.

### Workflow

1. **Code Push**: Push code changes to the connected GitHub repository
2. **Build Trigger**: Render automatically detects changes and initiates a build
3. **Docker Build**: Builds Docker image using the Dockerfile
4. **Kubernetes Deployment**: Creates or updates Kubernetes resources
5. **Health Checks**: Verifies application health before completing deployment
6. **Rollback**: Automatic rollback if deployment fails

### Configuration

The CI/CD pipeline is configured in `render.yaml`:

```yaml
services:
  - type: kubernetes
    name: clip-image-analysis
    env: docker
    dockerfilePath: ./Dockerfile
    k8sConfig:
      manifestPath: k8s.yaml
    envVars:
      - key: PYTHONHTTPSVERIFY
        value: "0"
      - key: HF_HUB_DISABLE_SSL_VERIFICATION
        value: "1"
      - key: PYTHONUNBUFFERED
        value: "1"
    healthCheckPath: /
    autoDeploy: true
```

### Preview Environments

Preview environments are automatically created for pull requests:

1. Create a new branch for feature development
2. Submit a pull request to the main branch
3. Render automatically creates a preview environment
4. Test the feature in the preview before merging
5. Preview environments automatically expire after a configurable period

## Kubernetes Deployment

The application is deployed on Render.com using Kubernetes for scalability and reliability.

### Kubernetes Resources

- **Deployment**: Manages the application pods
- **Service**: Exposes the application to the internet
- **ConfigMap**: Stores configuration data
- **PersistentVolumeClaim**: Stores model files persistently
- **HorizontalPodAutoscaler**: Automatically scales pods based on CPU usage

### Deployment Process

1. Push your code to GitHub
2. Connect your GitHub repository to Render.com
3. Render automatically deploys the application using the configuration in `render.yaml` and `k8s.yaml`
4. Monitor deployment status in the Render dashboard

### Manual Deployment (Optional)

If you prefer manual deployment or need to deploy from local:

```bash
# Install Render CLI
pip install render

# Log in
render login

# Deploy using your Kubernetes config
render deploy
```

### Scaling Configuration

The application automatically scales based on CPU usage:

- **Minimum Replicas**: 1
- **Maximum Replicas**: 3
- **Target CPU Utilization**: 80%

## Monitoring

The application includes Prometheus monitoring for performance tracking.

### Available Metrics

- **Image Upload Rate**: Number of images uploaded over time
- **Analysis Error Rate**: Percentage of analysis requests that result in errors
- **Analysis Duration**: Time taken to analyze images
- **Memory Usage**: Application memory consumption
- **CPU Usage**: Application CPU utilization

### Viewing Metrics

1. Access Prometheus metrics at `http://<your-app-url>:8000/metrics`
2. For Render deployments, metrics can be accessed through the Render dashboard

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**:
   - The application includes `ssl_fix.py` to handle certificate issues
   - Ensure environment variables `PYTHONHTTPSVERIFY=0` and `HF_HUB_DISABLE_SSL_VERIFICATION=1` are set

2. **Model Download Failures**:
   - Check internet connectivity
   - Verify Hugging Face is accessible from your deployment environment

3. **Kubernetes Deployment Issues**:
   - Check logs in the Render dashboard
   - Verify that the Kubernetes configuration in `k8s.yaml` is valid

### Getting Help

If you encounter issues not covered in this documentation, please:

1. Check the application logs in the Render dashboard
2. Open an issue in the GitHub repository with detailed error information
3. Include deployment environment details when reporting issues
