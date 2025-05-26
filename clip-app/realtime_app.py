# Real-time Web Application with Kafka Integration
# This FastAPI app handles image uploads, sends them to Kafka, and provides real-time results via WebSockets

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List
import threading
import time
import redis

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Import Kafka components
from kafka_config import KafkaImageProducer, KafkaResultsConsumer

# Import metrics if available
try:
    import metrics
    metrics_available = True
except ImportError:
    metrics_available = False

app = FastAPI(title="Real-time CLIP Image Analysis", version="1.0.0")

# Store for active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        # Use Redis for shared state across multiple webapp instances
        self.redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        print("✅ Redis connection established for shared state")
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"🔌 User {user_id} connected via WebSocket")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Clean up user requests from Redis
        try:
            self.redis_client.delete(f"user_requests:{user_id}")
        except Exception as e:
            print(f"❌ Error cleaning up Redis for user {user_id}: {e}")
        print(f"🔌 User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: dict):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Error broadcasting to {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    def add_request_for_user(self, user_id: str, request_id: str):
        try:
            # Store in Redis: user_requests:user_id -> list of request_ids
            key = f"user_requests:{user_id}"
            self.redis_client.lpush(key, request_id)
            self.redis_client.expire(key, 3600)  # Expire after 1 hour
            print(f"🔗 Added request {request_id} for user {user_id} in Redis")
            
            # Also create reverse mapping: request_id -> user_id
            reverse_key = f"request_user:{request_id}"
            self.redis_client.set(reverse_key, user_id, ex=3600)  # Expire after 1 hour
            print(f"🔗 Created reverse mapping {request_id} -> {user_id} in Redis")
        except Exception as e:
            print(f"❌ Error storing request mapping in Redis: {e}")
    
    def get_user_for_request(self, request_id: str) -> str:
        try:
            # Use reverse mapping for faster lookup
            reverse_key = f"request_user:{request_id}"
            user_id = self.redis_client.get(reverse_key)
            
            print(f"🔍 Looking for user for request {request_id}")
            if user_id:
                print(f"✅ Found user {user_id} for request {request_id} in Redis")
                return user_id
            else:
                print(f"❌ No user found for request {request_id} in Redis")
                return None
        except Exception as e:
            print(f"❌ Error retrieving user mapping from Redis: {e}")
            return None

# Global instances
manager = ConnectionManager()
kafka_producer = None
kafka_results_consumer = None

# Initialize Kafka connections
def init_kafka():
    global kafka_producer, kafka_results_consumer
    try:
        kafka_producer = KafkaImageProducer()
        kafka_results_consumer = KafkaResultsConsumer(group_id='webapp-results')
        print("✅ Kafka connections initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Kafka: {e}")
        raise

# Results consumer function
def consume_results():
    """Background task to consume analysis results from Kafka."""
    print("🎧 Starting results consumer...")
    
    def handle_result(result_data):
        """Handle incoming analysis results."""
        request_id = result_data['request_id']
        user_id = manager.get_user_for_request(request_id)
        
        print(f"📨 Received analysis result: {request_id}")
        
        if user_id:
            # Send result to specific user via WebSocket
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                loop.run_until_complete(
                    manager.send_personal_message({
                        'type': 'analysis_result',
                        'request_id': request_id,
                        'data': result_data
                    }, user_id)
                )
                
                # Also broadcast general stats
                loop.run_until_complete(
                    manager.broadcast({
                        'type': 'system_stats',
                        'data': {
                            'total_processed': 1,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    })
                )
                
                loop.close()
                print(f"✅ Result sent to user {user_id}")
                
            except Exception as e:
                print(f"❌ Error processing result: {e}")
        else:
            print(f"⚠️ No user found for request {request_id}")
    
    try:
        kafka_results_consumer.consume_results(handle_result)
    except Exception as e:
        print(f"❌ Error in results consumer: {e}")

# Start background task for consuming results
def start_background_tasks():
    """Start background tasks."""
    results_thread = threading.Thread(target=consume_results, daemon=True)
    results_thread.start()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 Starting Real-time CLIP Analysis API")
    init_kafka()
    start_background_tasks()
    
    if metrics_available:
        metrics.init_metrics()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down services...")
    if kafka_producer:
        kafka_producer.close()
    if kafka_results_consumer:
        kafka_results_consumer.close()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, user_id)
    
    # Send welcome message
    await manager.send_personal_message({
        'type': 'connection_established',
        'message': 'Connected to real-time CLIP analysis service'
    }, user_id)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'ping':
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                }, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.post("/upload_image")
async def upload_image(request: Request):
    """Upload an image for analysis."""
    try:
        # Parse form data manually
        form = await request.form()
        file = form.get("file")
        user_id = form.get("user_id", "anonymous")
        
        print(f"🔍 Received upload from user_id: {user_id}")
        print(f"🔍 Form data keys: {list(form.keys())}")
        
        if not file or not hasattr(file, 'content_type'):
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Send to Kafka for processing
        request_id = kafka_producer.send_image_for_analysis(
            image_data=image_data,
            filename=file.filename,
            user_id=user_id
        )
        
        # Track request for user
        manager.add_request_for_user(user_id, request_id)
        
        # Send immediate response
        await manager.send_personal_message({
            'type': 'upload_received',
            'request_id': request_id,
            'filename': file.filename,
            'message': 'Image received and queued for processing'
        }, user_id)
        
        # Update metrics
        if metrics_available:
            metrics.record_upload()
        
        return {
            "status": "success",
            "request_id": request_id,
            "message": "Image uploaded and queued for processing"
        }
        
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        
        if metrics_available:
            metrics.ANALYSIS_ERRORS.inc()
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "kafka_connected": kafka_producer is not None,
        "active_connections": len(manager.active_connections)
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "active_connections": len(manager.active_connections),
        "total_users": len(manager.user_requests),
        "kafka_connected": kafka_producer is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def get():
    """Serve the main HTML page."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-time CLIP Image Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .upload-area {
            border: 3px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #667eea;
            background-color: #f8f9ff;
        }
        .upload-area.dragover {
            border-color: #667eea;
            background-color: #f0f4ff;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .upload-btn:hover {
            transform: translateY(-2px);
        }
        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .status.connected {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.disconnected {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .results-container {
            margin-top: 30px;
        }
        .result-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #667eea;
        }
        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }
        .result-title {
            font-weight: bold;
            font-size: 1.1em;
        }
        .result-time {
            color: #666;
            font-size: 0.9em;
        }
        .predictions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }
        .prediction {
            background: white;
            padding: 10px 15px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .confidence {
            font-weight: bold;
            color: #667eea;
        }
        .processing {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖼️ Real-time CLIP Analysis</h1>
            <p>Upload images and get instant AI-powered analysis using Kafka streaming</p>
        </div>
        
        <div id="connection-status" class="status disconnected">
            🔌 Connecting to real-time service...
        </div>
        
        <div class="upload-area" id="upload-area">
            <h3>📁 Drop an image here or click to browse</h3>
            <p>Supported formats: JPEG, PNG, GIF</p>
            <input type="file" id="file-input" class="file-input" accept="image/*">
            <button class="upload-btn" onclick="document.getElementById('file-input').click()">
                Choose Image
            </button>
        </div>
        
        <div class="results-container">
            <h2>📊 Analysis Results</h2>
            <div id="results"></div>
        </div>
    </div>

    <script>
        const userId = 'user_' + Math.random().toString(36).substr(2, 9);
        let ws = null;
        let pendingUploads = new Set();

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${userId}`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                updateConnectionStatus(true);
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };
            
            ws.onclose = function(event) {
                updateConnectionStatus(false);
                setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus(false);
            };
        }

        function updateConnectionStatus(connected) {
            const statusDiv = document.getElementById('connection-status');
            if (connected) {
                statusDiv.className = 'status connected';
                statusDiv.innerHTML = '✅ Connected to real-time service';
            } else {
                statusDiv.className = 'status disconnected';
                statusDiv.innerHTML = '❌ Disconnected from real-time service';
            }
        }

        function handleWebSocketMessage(message) {
            switch(message.type) {
                case 'connection_established':
                    console.log('WebSocket connection established');
                    break;
                    
                case 'upload_received':
                    showProcessingStatus(message.request_id, message.filename);
                    break;
                    
                case 'analysis_result':
                    showAnalysisResult(message.data);
                    pendingUploads.delete(message.request_id);
                    break;
            }
        }

        function showProcessingStatus(requestId, filename) {
            const resultsDiv = document.getElementById('results');
            const processingDiv = document.createElement('div');
            processingDiv.id = `processing-${requestId}`;
            processingDiv.className = 'result-item';
            processingDiv.innerHTML = `
                <div class="result-header">
                    <span class="result-title">📷 ${filename}</span>
                    <span class="result-time">Processing...</span>
                </div>
                <div class="processing">
                    <span class="spinner"></span> Analyzing image with CLIP model...
                </div>
            `;
            resultsDiv.insertBefore(processingDiv, resultsDiv.firstChild);
            pendingUploads.add(requestId);
        }

        function showAnalysisResult(result) {
            const processingDiv = document.getElementById(`processing-${result.request_id}`);
            if (processingDiv) {
                processingDiv.remove();
            }

            const resultsDiv = document.getElementById('results');
            const resultDiv = document.createElement('div');
            resultDiv.className = 'result-item';
            
            const processingTime = result.processing_time ? `(${result.processing_time.toFixed(2)}s)` : '';
            const timestamp = new Date(result.timestamp).toLocaleTimeString();
            
            if (result.error) {
                resultDiv.innerHTML = `
                    <div class="result-header">
                        <span class="result-title">❌ Analysis Failed</span>
                        <span class="result-time">${timestamp}</span>
                    </div>
                    <div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 5px;">
                        Error: ${result.error}
                    </div>
                `;
            } else {
                const predictionsHtml = result.results.map(pred => `
                    <div class="prediction">
                        <span>${pred.label}</span>
                        <span class="confidence">${pred.confidence}%</span>
                    </div>
                `).join('');
                
                resultDiv.innerHTML = `
                    <div class="result-header">
                        <span class="result-title">✅ Analysis Complete ${processingTime}</span>
                        <span class="result-time">${timestamp}</span>
                    </div>
                    <div class="predictions">
                        ${predictionsHtml}
                    </div>
                `;
            }
            
            resultsDiv.insertBefore(resultDiv, resultsDiv.firstChild);
        }

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('user_id', userId);

            try {
                const response = await fetch('/upload_image', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Upload failed: ${response.statusText}`);
                }

                const result = await response.json();
                console.log('Upload successful:', result);
            } catch (error) {
                console.error('Upload error:', error);
                alert(`Upload failed: ${error.message}`);
            }
        }

        // File upload handlers
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');

        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0]);
            }
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                uploadFile(files[0]);
            }
        });

        // Initialize WebSocket connection
        connectWebSocket();

        // Keep connection alive
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'ping'}));
            }
        }, 30000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(
        "realtime_app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
