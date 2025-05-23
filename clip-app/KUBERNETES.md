# Kubernetes Deployment for CLIP Image Analysis App

This document describes how to deploy the CLIP Image Analysis application using Kubernetes.

## Prerequisites

1. A Kubernetes cluster (local like Minikube/kind or cloud-based)
2. kubectl installed and configured
3. Docker installed for building the image

## Deployment Steps

### 1. Build the Docker image

```bash
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

### 3. Apply the Kubernetes manifests

```bash
kubectl apply -f k8s-configmap.yaml
kubectl apply -f k8s-pvc.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
kubectl apply -f k8s-hpa.yaml
```

### 4. Access the application

```bash
# For Minikube
minikube service clip-app-service

# For regular Kubernetes, get the external IP
kubectl get service clip-app-service
```

## Verify Deployment

```bash
# Check if pods are running
kubectl get pods

# Check service status
kubectl get service

# Check HPA status
kubectl get hpa

# View pod logs
kubectl logs -f deployment/clip-app
```

## Scaling

The Horizontal Pod Autoscaler (HPA) will automatically scale the deployment based on CPU utilization. You can manually scale the deployment with:

```bash
kubectl scale deployment clip-app --replicas=3
```

## Cleaning Up

```bash
kubectl delete -f k8s-hpa.yaml
kubectl delete -f k8s-service.yaml
kubectl delete -f k8s-deployment.yaml
kubectl delete -f k8s-pvc.yaml
kubectl delete -f k8s-configmap.yaml
```
