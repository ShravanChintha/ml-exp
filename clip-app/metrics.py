# Monitoring for CLIP Image Analysis App in Kubernetes

import streamlit as st
import psutil
import time
import threading
import socket
import os
from prometheus_client import start_http_server, Counter, Gauge, Histogram, Summary

# Define metrics
IMAGE_UPLOADS = Counter('clip_image_uploads_total', 'Total number of images uploaded')
ANALYSIS_REQUESTS = Counter('clip_analysis_requests_total', 'Total number of analysis requests')
ANALYSIS_ERRORS = Counter('clip_analysis_errors_total', 'Total number of analysis errors')
ANALYSIS_DURATION = Histogram('clip_analysis_duration_seconds', 'Time spent processing images',
                           buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0])
MEMORY_USAGE = Gauge('clip_memory_usage_bytes', 'Memory usage of the application')
CPU_USAGE = Gauge('clip_cpu_usage_percent', 'CPU usage percentage of the application')
ACTIVE_USERS = Gauge('clip_active_users', 'Number of currently active users')

# Start Prometheus metrics server on port 8000
def start_metrics_server():
    try:
        start_http_server(8000)
        print("Prometheus metrics server started on port 8000")
    except Exception as e:
        print(f"Failed to start metrics server: {e}")

# Update system metrics periodically
def collect_system_metrics():
    while True:
        try:
            # Update memory usage
            MEMORY_USAGE.set(psutil.Process(os.getpid()).memory_info().rss)
            
            # Update CPU usage
            CPU_USAGE.set(psutil.Process(os.getpid()).cpu_percent(interval=1.0))
            
            time.sleep(15)
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            time.sleep(15)

# Initialize metrics collection
def init_metrics():
    # Start metrics server in a separate thread
    server_thread = threading.Thread(target=start_metrics_server, daemon=True)
    server_thread.start()
    
    # Start system metrics collection in a separate thread
    metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
    metrics_thread.start()
    
    # Log startup
    hostname = socket.gethostname()
    print(f"Metrics initialized on host: {hostname}")

# Call this function when analyzing an image
def record_analysis(func):
    def wrapper(*args, **kwargs):
        ANALYSIS_REQUESTS.inc()
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            ANALYSIS_DURATION.observe(duration)
            return result
        except Exception as e:
            ANALYSIS_ERRORS.inc()
            raise e
    return wrapper

# Call this when an image is uploaded
def record_upload():
    IMAGE_UPLOADS.inc()

# Call this when a user session starts
def user_connected():
    ACTIVE_USERS.inc()

# Call this when a user session ends
def user_disconnected():
    if ACTIVE_USERS._value > 0:
        ACTIVE_USERS.dec()

# Initialize metrics at startup
init_metrics()
