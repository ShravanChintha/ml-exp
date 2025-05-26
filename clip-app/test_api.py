#!/usr/bin/env python3
"""
Simple test client for the CLIP Analysis API
This demonstrates how to use the API step by step
"""

import requests
import time
import json
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8080"

def test_api_step_by_step():
    """Demonstrate the complete API workflow step by step."""
    
    print("🚀 Testing Simple CLIP Analysis API")
    print("=" * 50)
    
    # Step 1: Check if API is running
    print("\n📡 Step 1: Checking API health...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API is running!")
            print(f"📋 Available endpoints: {response.json()['endpoints']}")
        else:
            print("❌ API not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on localhost:8080")
        return
    
    # Step 2: Upload an image
    print("\n📤 Step 2: Uploading image for analysis...")
    
    # Use the test image in the project
    image_path = Path("test_image.jpg")
    if not image_path.exists():
        print("❌ test_image.jpg not found. Please add an image file to test with.")
        return
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/analyze-image", files=files)
        
        if response.status_code == 200:
            result = response.json()
            request_id = result['request_id']
            print(f"✅ Image uploaded successfully!")
            print(f"📝 Request ID: {request_id}")
            print(f"📊 File size: {result['size_bytes']} bytes")
            
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return
    
    # Step 3: Check status periodically
    print(f"\n🔍 Step 3: Monitoring analysis progress...")
    max_attempts = 30  # Wait up to 30 seconds
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE}/status/{request_id}")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data['status']
                
                print(f"📊 Attempt {attempt + 1}: Status = {status}")
                
                if status == "completed":
                    print("✅ Analysis completed!")
                    break
                elif status == "not_found":
                    print("❌ Request not found")
                    return
                else:
                    print(f"⏳ Still {status}, waiting 2 seconds...")
                    time.sleep(2)
                    
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return
        
        attempt += 1
    
    if attempt >= max_attempts:
        print("⏰ Timeout waiting for analysis to complete")
        return
    
    # Step 4: Get the results
    print(f"\n📊 Step 4: Retrieving analysis results...")
    try:
        response = requests.get(f"{API_BASE}/result/{request_id}")
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis Results:")
            print("=" * 30)
            
            analysis = result['analysis']
            metadata = result['metadata']
            
            print(f"🖼️  Image: {metadata['filename']}")
            print(f"⏱️  Processing time: {analysis['processing_time_seconds']:.2f} seconds")
            print(f"🎯 Top prediction: {analysis['top_prediction']}")
            
            print("\n🏆 All predictions:")
            predictions = analysis['predictions']
            scores = analysis['confidence_scores']
            
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                print(f"  {i+1}. {pred}: {score:.1%}")
            
            print(f"\n📅 Analyzed at: {metadata['analyzed_at']}")
            
        else:
            print(f"❌ Failed to get results: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error getting results: {e}")
        return
    
    # Step 5: Check API stats
    print(f"\n📈 Step 5: Checking API statistics...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("📊 API Statistics:")
            print(f"  • Total requests: {stats['total_requests']}")
            print(f"  • Completed: {stats['completed_requests']}")
            print(f"  • Pending: {stats['pending_requests']}")
            print(f"  • Completion rate: {stats['completion_rate']:.1f}%")
            print(f"  • Kafka connected: {stats['active_kafka_connection']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    print("\n🎉 API test completed successfully!")


def quick_test():
    """Quick test with minimal output."""
    image_path = Path("test_image.jpg")
    if not image_path.exists():
        print("❌ test_image.jpg not found")
        return
    
    print("🚀 Quick API Test...")
    
    # Upload
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post(f"{API_BASE}/analyze-image", files=files)
    
    request_id = response.json()['request_id']
    print(f"📝 Request ID: {request_id}")
    
    # Wait for completion
    for i in range(20):
        response = requests.get(f"{API_BASE}/status/{request_id}")
        if response.json()['status'] == 'completed':
            break
        time.sleep(1)
    
    # Get result
    response = requests.get(f"{API_BASE}/result/{request_id}")
    result = response.json()
    
    print(f"🎯 Result: {result['analysis']['top_prediction']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        test_api_step_by_step()
