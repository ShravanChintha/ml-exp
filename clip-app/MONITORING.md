# Monitoring Setup for CLIP App Kubernetes Deployment

This document describes how to set up and use Prometheus and Grafana for monitoring your CLIP Image Analysis application on Kubernetes.

## Prerequisites

- A running Kubernetes cluster with your application deployed
- kubectl configured for your cluster

## Monitor Stack Deployment

Deploy the monitoring stack with these commands:

```bash
# Apply Prometheus RBAC
kubectl apply -f k8s-prometheus-rbac.yaml

# Apply Prometheus ConfigMap
kubectl apply -f k8s-prometheus-configmap.yaml

# Deploy Prometheus
kubectl apply -f k8s-prometheus.yaml

# Deploy Grafana
kubectl apply -f k8s-grafana.yaml
```

## Accessing Monitoring Dashboards

### Prometheus

```bash
# Port-forward Prometheus service
kubectl port-forward svc/prometheus 9090:9090
```

Access Prometheus UI at http://localhost:9090

### Grafana

```bash
# Get Grafana external IP (if using LoadBalancer)
kubectl get svc grafana

# OR port-forward if needed
kubectl port-forward svc/grafana 3000:3000
```

Access Grafana at http://localhost:3000 or http://EXTERNAL-IP:3000

Default login:
- Username: admin
- Password: admin

## Setting Up Grafana Dashboards

After logging into Grafana:

1. Add Prometheus as a data source:
   - Go to Configuration (gear icon) > Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - Set URL to `http://prometheus:9090`
   - Click "Save & Test"

2. Import a Kubernetes dashboard:
   - Go to "+" icon > Import
   - Enter dashboard ID: 10856 (Kubernetes cluster monitoring) or 6417 (Pod monitoring)
   - Select your Prometheus data source
   - Click "Import"

## Useful Prometheus Queries

Here are some useful queries for monitoring your CLIP app:

- **CPU Usage by Pod**: 
  ```
  sum(rate(container_cpu_usage_seconds_total{pod=~"clip-app-.*"}[5m])) by (pod)
  ```

- **Memory Usage by Pod**:
  ```
  sum(container_memory_usage_bytes{pod=~"clip-app-.*"}) by (pod)
  ```

- **Pod Restarts**:
  ```
  kube_pod_container_status_restarts_total{pod=~"clip-app-.*"}
  ```

## Cleaning Up

```bash
kubectl delete -f k8s-grafana.yaml
kubectl delete -f k8s-prometheus.yaml
kubectl delete -f k8s-prometheus-configmap.yaml
kubectl delete -f k8s-prometheus-rbac.yaml
```
