#!/bin/bash

# CLIP App Kubernetes Deployment Script
# This script handles the complete deployment of the CLIP image analysis application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="clip-app"
APP_NAME="clip-app"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"localhost:5000"}  # Change this to your registry

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists kubectl; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build web app image
    print_status "Building CLIP web app image..."
    docker build -f Dockerfile.webapp -t clip-webapp:latest .
    
    # Build processor image
    print_status "Building CLIP processor image..."
    docker build -f Dockerfile.processor -t clip-processor:latest .
    
    print_success "Docker images built successfully"
}

# Load images to cluster (for kind/minikube)
load_images_to_cluster() {
    print_status "Loading images to cluster..."
    
    # Check if we're using kind
    if command_exists kind && kind get clusters >/dev/null 2>&1; then
        print_status "Detected kind cluster, loading images..."
        kind load docker-image clip-webapp:latest
        kind load docker-image clip-processor:latest
    elif command_exists minikube && minikube status >/dev/null 2>&1; then
        print_status "Detected minikube cluster, loading images..."
        minikube image load clip-webapp:latest
        minikube image load clip-processor:latest
    else
        print_warning "Cluster type not detected or images may need to be pushed to registry"
    fi
}

# Deploy to Kubernetes
deploy_to_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Apply the Kubernetes manifests
    kubectl apply -f k8s-complete.yaml
    
    print_success "Kubernetes manifests applied"
}

# Wait for deployments
wait_for_deployments() {
    print_status "Waiting for deployments to be ready..."
    
    # Wait for each deployment
    deployments=("zookeeper" "kafka" "redis" "clip-webapp" "clip-processor")
    
    for deployment in "${deployments[@]}"; do
        print_status "Waiting for $deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/$deployment -n $NAMESPACE
        if [ $? -eq 0 ]; then
            print_success "$deployment is ready"
        else
            print_error "$deployment failed to become ready within timeout"
            return 1
        fi
    done
    
    print_success "All deployments are ready"
}

# Setup port forwarding
setup_port_forwarding() {
    print_status "Setting up port forwarding..."
    
    # Kill any existing port forwards
    pkill -f "kubectl.*port-forward" 2>/dev/null || true
    
    # Port forward the web app
    kubectl port-forward -n $NAMESPACE service/clip-webapp 8080:80 &
    
    print_success "Port forwarding setup complete"
    print_status "Application will be available at: http://localhost:8080"
}

# Show status
show_status() {
    print_status "Application Status:"
    echo ""
    
    print_status "Pods:"
    kubectl get pods -n $NAMESPACE
    echo ""
    
    print_status "Services:"
    kubectl get services -n $NAMESPACE
    echo ""
    
    print_status "Ingress:"
    kubectl get ingress -n $NAMESPACE
    echo ""
    
    print_status "PVCs:"
    kubectl get pvc -n $NAMESPACE
}

# Cleanup function
cleanup() {
    print_status "Cleaning up CLIP application..."
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    print_success "Cleanup complete"
}

# Main deployment function
deploy() {
    print_status "Starting CLIP App deployment..."
    
    check_prerequisites
    build_images
    load_images_to_cluster
    deploy_to_k8s
    wait_for_deployments
    setup_port_forwarding
    show_status
    
    print_success "🎉 CLIP App deployment complete!"
    echo ""
    print_status "Access the application at: http://localhost:8080"
    print_status "Use 'kubectl logs -f deployment/clip-webapp -n $NAMESPACE' to view web app logs"
    print_status "Use 'kubectl logs -f deployment/clip-processor -n $NAMESPACE' to view processor logs"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "cleanup")
        cleanup
        ;;
    "status")
        show_status
        ;;
    "logs-webapp")
        kubectl logs -f deployment/clip-webapp -n $NAMESPACE
        ;;
    "logs-processor")
        kubectl logs -f deployment/clip-processor -n $NAMESPACE
        ;;
    "port-forward")
        setup_port_forwarding
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|status|logs-webapp|logs-processor|port-forward}"
        echo ""
        echo "Commands:"
        echo "  deploy        - Deploy the complete CLIP application"
        echo "  cleanup       - Remove the CLIP application from cluster"
        echo "  status        - Show application status"
        echo "  logs-webapp   - Follow web application logs"
        echo "  logs-processor- Follow image processor logs"
        echo "  port-forward  - Setup port forwarding to access the app"
        exit 1
        ;;
esac
