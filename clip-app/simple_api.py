#!/usr/bin/env python3
"""
Simple API-only version of the CLIP Image Analysis System
This demonstrates the core Kafka + AI workflow without WebSocket complexity
"""

import os
import json
import uuid
import base64
import time
from datetime import datetime
from typing import Optional, Dict, List
import asyncio
import threading

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

# Import Kafka components
from kafka_config import KafkaImageProducer, KafkaResultsConsumer

# Simple in-memory storage for demo (use Redis in production)
analysis_results: Dict[str, dict] = {}
pending_requests: Dict[str, dict] = {}

app = FastAPI(
    title="Simple CLIP Analysis API",
    description="REST API for real-time image analysis using CLIP model via Kafka",
    version="1.0.0"
)

# Global Kafka instances
kafka_producer: Optional[KafkaImageProducer] = None
kafka_results_consumer: Optional[KafkaResultsConsumer] = None


def init_kafka():
    """Initialize Kafka producer and consumer."""
    global kafka_producer, kafka_results_consumer
    try:
        kafka_producer = KafkaImageProducer()
        kafka_results_consumer = KafkaResultsConsumer(group_id='simple-api-results')
        print("✅ Kafka connections initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Kafka: {e}")
        raise


def handle_analysis_result(result_data: dict):
    """Handle analysis results from Kafka consumer."""
    request_id = result_data.get('request_id')
    if request_id:
        # Store result for retrieval
        analysis_results[request_id] = result_data
        # Remove from pending
        pending_requests.pop(request_id, None)
        print(f"✅ Stored analysis result for request: {request_id}")


def consume_results_background():
    """Background task to consume analysis results from Kafka."""
    print("🎧 Starting background results consumer...")
    try:
        kafka_results_consumer.consume_results(handle_analysis_result)
    except Exception as e:
        print(f"❌ Error in results consumer: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 Starting Simple CLIP Analysis API")
    init_kafka()
    
    # Start background consumer in a separate thread
    consumer_thread = threading.Thread(target=consume_results_background, daemon=True)
    consumer_thread.start()
    
    print("✅ API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down services...")
    if kafka_producer:
        kafka_producer.close()
    if kafka_results_consumer:
        kafka_results_consumer.close()


@app.get("/")
async def root():
    """API health check and info."""
    return {
        "message": "Simple CLIP Analysis API",
        "status": "running",
        "endpoints": {
            "upload": "POST /analyze-image - Upload image for analysis",
            "status": "GET /status/{request_id} - Check analysis status",
            "result": "GET /result/{request_id} - Get analysis result",
            "stats": "GET /stats - Get API statistics"
        }
    }


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Upload an image for CLIP analysis.
    
    Returns:
        request_id: Use this to check status and get results
    """
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request info
        pending_requests[request_id] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(image_data),
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted"
        }
        
        # Send to Kafka for processing
        success = kafka_producer.send_image_for_analysis(
            image_data=image_data,
            filename=file.filename,
            request_id=request_id,
            user_id="api-user"  # Simple user ID for API mode
        )
        
        if success:
            pending_requests[request_id]["status"] = "processing"
            print(f"📤 Sent image for analysis: {request_id}")
            
            return JSONResponse(content={
                "request_id": request_id,
                "status": "accepted",
                "message": "Image submitted for analysis",
                "filename": file.filename,
                "size_bytes": len(image_data)
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to submit image for processing")
            
    except Exception as e:
        print(f"❌ Error in analyze_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{request_id}")
async def get_status(request_id: str):
    """
    Check the status of an analysis request.
    
    Returns:
        - pending: Request is in queue
        - processing: AI model is analyzing the image
        - completed: Analysis is done, result available
        - not_found: Request ID not found
    """
    # Check if completed
    if request_id in analysis_results:
        return {
            "request_id": request_id,
            "status": "completed",
            "result_available": True,
            "completed_at": analysis_results[request_id].get('timestamp')
        }
    
    # Check if pending/processing
    if request_id in pending_requests:
        return {
            "request_id": request_id,
            "status": pending_requests[request_id]["status"],
            "result_available": False,
            "submitted_at": pending_requests[request_id]["submitted_at"]
        }
    
    # Not found
    return {
        "request_id": request_id,
        "status": "not_found",
        "result_available": False
    }


@app.get("/result/{request_id}")
async def get_result(request_id: str):
    """
    Get the analysis result for a completed request.
    
    Returns:
        Detailed analysis results from CLIP model
    """
    if request_id not in analysis_results:
        if request_id in pending_requests:
            raise HTTPException(
                status_code=202,  # Accepted but not ready
                detail="Analysis still in progress. Check /status/{request_id}"
            )
        else:
            raise HTTPException(status_code=404, detail="Request ID not found")
    
    result = analysis_results[request_id]
    
    return {
        "request_id": request_id,
        "status": "completed",
        "analysis": {
            "predictions": result.get('predictions', []),
            "confidence_scores": result.get('confidence_scores', []),
            "top_prediction": result.get('top_prediction'),
            "processing_time_seconds": result.get('processing_time_seconds'),
            "model_info": result.get('model_info', {})
        },
        "metadata": {
            "filename": result.get('filename'),
            "analyzed_at": result.get('timestamp'),
            "image_dimensions": result.get('image_dimensions')
        }
    }


@app.get("/stats")
async def get_stats():
    """Get API usage statistics."""
    total_requests = len(pending_requests) + len(analysis_results)
    completed_requests = len(analysis_results)
    pending_count = len(pending_requests)
    
    return {
        "total_requests": total_requests,
        "completed_requests": completed_requests,
        "pending_requests": pending_count,
        "completion_rate": completed_requests / max(total_requests, 1) * 100,
        "active_kafka_connection": kafka_producer is not None,
        "api_uptime": "See server logs"
    }


@app.delete("/cleanup")
async def cleanup_old_results():
    """Clean up old results (for demo purposes)."""
    old_count = len(analysis_results)
    analysis_results.clear()
    pending_requests.clear()
    
    return {
        "message": f"Cleaned up {old_count} old results",
        "remaining_results": len(analysis_results)
    }


if __name__ == "__main__":
    print("🚀 Starting Simple CLIP Analysis API")
    print("📖 API Documentation will be available at: http://localhost:8080/docs")
    print("🔧 Test the API with: curl -X POST -F 'file=@your_image.jpg' http://localhost:8080/analyze-image")
    
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
