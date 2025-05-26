# Kubernetes Deployment Guide for CLIP Image Analysis App

This guide provides step-by-step instructions to deploy the CLIP image analysis application on Kubernetes.

## Prerequisites

1. **Kubernetes Cluster**: You need access to a Kubernetes cluster (local or cloud-based)
2. **kubectl**: Kubernetes command-line tool
3. **Docker**: For building container images
4. **Cluster Types Supported**:
   - Local: kind, minikube, Docker Desktop
   - Cloud: GKE, EKS, AKS
   - On-premise: Any standard Kubernetes distribution

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Navigate to the project directory
cd /Users/shravan-chintha/Documents/ml-exp/clip-app

# Run the automated deployment script
./deploy-k8s.sh deploy
```

This script will:
- Build Docker images
- Deploy all services (Zookeeper, Kafka, Redis, Web App, Processor)
- Set up port forwarding
- Show deployment status

### Option 2: Manual Deployment

If you prefer manual control, follow these steps:

#### Step 1: Build Docker Images

```bash
# Build the web application image
docker build -f Dockerfile.webapp -t clip-webapp:latest .

# Build the image processor
docker build -f Dockerfile.processor -t clip-processor:latest .
```

#### Step 2: Load Images to Cluster (for local clusters)

**For kind:**
```bash
kind load docker-image clip-webapp:latest
kind load docker-image clip-processor:latest
```

**For minikube:**
```bash
minikube image load clip-webapp:latest
minikube image load clip-processor:latest
```

**For cloud clusters:**
```bash
# Tag and push to your container registry
docker tag clip-webapp:latest your-registry/clip-webapp:latest
docker tag clip-processor:latest your-registry/clip-processor:latest
docker push your-registry/clip-webapp:latest
docker push your-registry/clip-processor:latest

# Update k8s-complete.yaml to use your registry images
```

#### Step 3: Deploy to Kubernetes

```bash
# Apply the Kubernetes manifests
kubectl apply -f k8s-complete.yaml
```

#### Step 4: Wait for Deployment

```bash
# Check deployment status
kubectl get pods -n clip-app

# Wait for all pods to be ready
kubectl wait --for=condition=available --timeout=300s deployment/clip-webapp -n clip-app
kubectl wait --for=condition=available --timeout=300s deployment/clip-processor -n clip-app
kubectl wait --for=condition=available --timeout=300s deployment/kafka -n clip-app
kubectl wait --for=condition=available --timeout=300s deployment/zookeeper -n clip-app
kubectl wait --for=condition=available --timeout=300s deployment/redis -n clip-app
```

#### Step 5: Access the Application

```bash
# Set up port forwarding
kubectl port-forward -n clip-app service/clip-webapp 8080:80

# Access the application at http://localhost:8080
```

## Architecture Overview

The deployment includes the following components:

### Services:
- **clip-webapp**: FastAPI web application with WebSocket support
- **clip-processor**: CLIP model image processing service
- **kafka**: Message broker for async processing
- **zookeeper**: Kafka dependency
- **redis**: Caching and session storage

### Resources:
- **Namespace**: `clip-app` (isolated environment)
- **PVCs**: Persistent storage for models and data
- **HPA**: Auto-scaling based on CPU/memory usage
- **Ingress**: External access configuration

## Management Commands

```bash
# View application status
./deploy-k8s.sh status

# View web application logs
./deploy-k8s.sh logs-webapp

# View processor logs
./deploy-k8s.sh logs-processor

# Setup port forwarding
./deploy-k8s.sh port-forward

# Clean up deployment
./deploy-k8s.sh cleanup
```

## Manual kubectl Commands

```bash
# Get all resources in the clip-app namespace
kubectl get all -n clip-app

# Check pod logs
kubectl logs -f deployment/clip-webapp -n clip-app
kubectl logs -f deployment/clip-processor -n clip-app
kubectl logs -f deployment/kafka -n clip-app

# Check service endpoints
kubectl get endpoints -n clip-app

# Scale deployments
kubectl scale deployment clip-processor --replicas=3 -n clip-app

# Port forward to different services
kubectl port-forward -n clip-app service/kafka 9092:9092
kubectl port-forward -n clip-app service/redis 6379:6379

# Check resource usage
kubectl top pods -n clip-app
kubectl top nodes
```

## Ingress Configuration

For production deployment with external access:

1. **Install Ingress Controller** (if not already installed):
```bash
# For NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

2. **Update DNS** (for production):
   - Point `clip-app.local` to your ingress controller's external IP
   - Or update the ingress host in `k8s-complete.yaml`

3. **Access via Ingress**:
   - Local: Add `127.0.0.1 clip-app.local` to `/etc/hosts`
   - Production: Use your actual domain

## Troubleshooting

### Common Issues:

1. **Pods stuck in Pending state**:
   ```bash
   kubectl describe pod <pod-name> -n clip-app
   # Check for resource constraints or storage issues
   ```

2. **ImagePullBackOff errors**:
   - Ensure images are built and available
   - For local clusters, make sure images are loaded
   - For cloud, check registry authentication

3. **Kafka connection issues**:
   ```bash
   # Check if Kafka is ready
   kubectl logs deployment/kafka -n clip-app
   
   # Test Kafka connectivity from webapp pod
   kubectl exec -it deployment/clip-webapp -n clip-app -- nc -zv kafka 9092
   ```

4. **Model loading issues**:
   ```bash
   # Check PVC mount
   kubectl describe pvc clip-model-storage -n clip-app
   
   # Check if models directory is accessible
   kubectl exec -it deployment/clip-processor -n clip-app -- ls -la /app/models
   ```

### Monitoring:

```bash
# Watch pod status in real-time
kubectl get pods -n clip-app -w

# Monitor resource usage
kubectl top pods -n clip-app --sort-by=cpu
kubectl top pods -n clip-app --sort-by=memory

# Check events
kubectl get events -n clip-app --sort-by='.lastTimestamp'
```

## Scaling

The deployment includes Horizontal Pod Autoscalers (HPA) that automatically scale based on resource usage:

- **Web App**: 2-5 replicas (scales on CPU 70%, Memory 80%)
- **Processor**: 2-10 replicas (scales on CPU 75%)

Manual scaling:
```bash
# Scale web application
kubectl scale deployment clip-webapp --replicas=3 -n clip-app

# Scale image processor
kubectl scale deployment clip-processor --replicas=5 -n clip-app
```

## Production Considerations

1. **Resource Limits**: Adjust CPU/memory limits based on your workload
2. **Storage**: Use appropriate storage classes for your environment
3. **Security**: Configure network policies, RBAC, and pod security policies
4. **Monitoring**: Set up Prometheus, Grafana, or other monitoring solutions
5. **Backup**: Regular backup of persistent volumes
6. **SSL/TLS**: Configure SSL certificates for production ingress

## Cleanup

To remove the entire deployment:

```bash
./deploy-k8s.sh cleanup
```

Or manually:
```bash
kubectl delete namespace clip-app
```

This will remove all resources including persistent volumes and data.
