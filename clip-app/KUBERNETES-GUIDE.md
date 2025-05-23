# Kubernetes Deployment Guide for CLIP Image Analysis App

This guide explains how to deploy the CLIP Image Analysis application to Kubernetes using a single consolidated YAML file.

## Prerequisites

1. A Kubernetes cluster (local like Minikube/kind or cloud-based)
2. kubectl installed and configured
3. Docker installed for building the image

## Understanding the Deployment Architecture

The consolidated YAML file (`clip-app-kubernetes.yaml`) contains all necessary resources for both the application and monitoring stack:

1. **Application Components**:
   - **ConfigMap**: Environment variables and configuration
   - **PersistentVolumeClaim**: Persistent storage for model files
   - **Deployment**: The application container definition
   - **Service**: External access to the application
   - **HorizontalPodAutoscaler**: Automatic scaling based on CPU usage

2. **Monitoring Components**:
   - **Prometheus**: Metrics collection and storage
   - **Grafana**: Metrics visualization and dashboards
   - **RBAC Resources**: Permissions for Prometheus to access Kubernetes API

## Deployment Steps

### 1. Build the Docker image

```bash
cd /Users/shravan.chintha/Desktop/ML/FastAPI-for-ML
docker build -t clip-app:latest .
```

### 2. Load the image into your Kubernetes cluster

If using Minikube:
```bash
minikube image load clip-app:latest
```

If using kind:
```bash
kind load docker-image clip-app:latest
```

### 3. Apply the consolidated YAML file

```bash
kubectl apply -f clip-app-kubernetes.yaml
```

This single command will create all necessary resources in the correct order.

### 4. Verify the deployment

Check that all resources were created successfully:

```bash
# Check all resources with the app=clip-app label
kubectl get all -l app=clip-app

# Check all resources with the app=monitoring label
kubectl get all -l app=monitoring

# Check persistent volume claims
kubectl get pvc

# Check config maps
kubectl get configmap

# Check horizontal pod autoscaler
kubectl get hpa
```

### 5. Access the application

```bash
# Get the external IP of the clip-app-service
kubectl get service clip-app-service
```

Access the application at `http://<EXTERNAL-IP>:8501`

For Minikube, use:
```bash
minikube service clip-app-service
```

### 6. Access the monitoring dashboards

For Prometheus:
```bash
kubectl port-forward svc/prometheus 9090:9090
```
Access at http://localhost:9090

For Grafana:
```bash
kubectl port-forward svc/grafana 3000:3000
```
Access at http://localhost:3000 with username `admin` and password `admin`

## Configuring Grafana

After accessing Grafana:

1. Add Prometheus as a data source:
   - Go to Configuration > Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - URL: `http://prometheus:9090`
   - Click "Save & Test"

2. Import a dashboard:
   - Go to Create > Import
   - Enter dashboard ID: 10856 (Kubernetes cluster monitoring)
   - Select your Prometheus data source
   - Click "Import"

## Key Application Metrics

In Prometheus or Grafana, you can query these metrics:

- **Image Upload Rate**: `rate(clip_image_uploads_total[5m])`
- **Analysis Error Rate**: `rate(clip_analysis_errors_total[5m]) / rate(clip_analysis_requests_total[5m])`
- **Analysis Duration**: `histogram_quantile(0.95, sum(rate(clip_analysis_duration_seconds_bucket[5m])) by (le))`
- **Memory Usage**: `clip_memory_usage_bytes` or `container_memory_usage_bytes{pod=~"clip-app.*"}`
- **CPU Usage**: `clip_cpu_usage_percent` or `rate(container_cpu_usage_seconds_total{pod=~"clip-app.*"}[5m])`

## Cleaning Up

To remove all resources:

```bash
kubectl delete -f clip-app-kubernetes.yaml
```

## Troubleshooting

If you encounter issues:

```bash
# Check pod status
kubectl describe pod -l app=clip-app

# Check logs
kubectl logs -l app=clip-app

# Check events
kubectl get events
```
