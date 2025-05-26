# CLIP Image Processor Service - Kafka Consumer
# This service consumes images from Kafka and processes them with CLIP model

import os
import sys
import time
import base64
import io
from PIL import Image
import torch
import signal
import threading
from datetime import datetime

# Import SSL fix first
try:
    import ssl_fix
    print("SSL certificate verification disabled - Running in insecure mode")
except ImportError:
    print("WARNING: SSL fix module not found, continuing with default SSL settings")

# Import nest_asyncio fix
import nest_asyncio
nest_asyncio.apply()

# Try to import CLIP modules
try:
    from transformers import CLIPProcessor, CLIPModel
    print("Successfully imported CLIP modules")
except ImportError as e:
    print(f"Error importing CLIP modules: {str(e)}")
    sys.exit(1)

# Import Kafka components
from kafka_config import KafkaImageConsumer, KafkaResultsProducer

class CLIPImageProcessor:
    """Service that processes images using CLIP model."""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.consumer = None
        self.results_producer = None
        self.running = False
        self.load_model()
        self.setup_kafka()
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_model(self):
        """Load the CLIP model and processor."""
        try:
            print("🔄 Loading CLIP model...")
            
            # Disable SSL verification for Hugging Face
            os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'
            
            model_id = "openai/clip-vit-base-patch32"
            
            # Try to load from local cache first
            cache_dir = os.path.join(os.path.dirname(__file__), "models")
            model_cache = os.path.join(cache_dir, "clip-model")
            processor_cache = os.path.join(cache_dir, "clip-processor")
            
            if os.path.exists(model_cache) and os.path.exists(processor_cache):
                print("📁 Loading model from local cache...")
                self.model = CLIPModel.from_pretrained(model_cache)
                self.processor = CLIPProcessor.from_pretrained(processor_cache)
            else:
                print("🌐 Downloading model from Hugging Face...")
                self.model = CLIPModel.from_pretrained(
                    model_id, 
                    trust_remote_code=True,
                    force_download=False
                )
                self.processor = CLIPProcessor.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    force_download=False
                )
                
                # Save to cache
                os.makedirs(model_cache, exist_ok=True)
                os.makedirs(processor_cache, exist_ok=True)
                self.model.save_pretrained(model_cache)
                self.processor.save_pretrained(processor_cache)
                print("💾 Model saved to local cache")
            
            print("✅ CLIP model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading CLIP model: {e}")
            sys.exit(1)
    
    def setup_kafka(self):
        """Setup Kafka consumer and producer."""
        try:
            print("🔄 Setting up Kafka connections...")
            self.consumer = KafkaImageConsumer(group_id='clip-processors')
            self.results_producer = KafkaResultsProducer()
            print("✅ Kafka connections established")
            
        except Exception as e:
            print(f"❌ Error setting up Kafka: {e}")
            sys.exit(1)
    
    def analyze_image(self, image_data):
        """Analyze image using CLIP model."""
        try:
            start_time = time.time()
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Candidate labels for classification
            candidate_labels = [
                "a photo of a person", "a photo of a landscape", "a photo of an animal",
                "a photo of food", "a photo of a building", "a photo of a vehicle",
                "a photo of nature", "a photo of technology", "a photo of art",
                "a photo of sports", "a photo of water", "a photo of mountains",
                "a photo of a city", "a photo of a beach", "a photo of flowers",
                "a photo of a cat", "a photo of a dog", "a photo of a bird",
                "a photo of text", "a photo of clothing", "a photo of furniture",
                "a photo of electronics", "a photo of toys", "a photo of tools",
                "a photo of outdoor scene", "a photo of indoor scene", "a photo of abstract art"
            ]
            
            # Process the image and text
            inputs = self.processor(
                text=candidate_labels,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Get top 8 predictions
            top_probs, top_indices = torch.topk(probs[0], k=8)
            
            results = []
            for prob, idx in zip(top_probs, top_indices):
                label = candidate_labels[idx]
                confidence = prob.item() * 100
                # Remove "a photo of" prefix for display
                clean_label = label.replace("a photo of ", "")
                results.append({
                    "label": clean_label,
                    "confidence": round(confidence, 2)
                })
            
            processing_time = time.time() - start_time
            
            return results, processing_time
            
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            raise
    
    def process_image_message(self, message_data):
        """Process a single image message from Kafka."""
        request_id = message_data['request_id']
        user_id = message_data['user_id']
        filename = message_data['filename']
        
        print(f"🖼️  Processing image: {filename} (ID: {request_id[:8]}...)")
        
        try:
            # Analyze the image
            results, processing_time = self.analyze_image(message_data['image_data'])
            
            # Send results back to Kafka
            self.results_producer.send_analysis_result(
                request_id=request_id,
                results=results,
                user_id=user_id,
                processing_time=processing_time
            )
            
            print(f"✅ Completed processing: {filename} in {processing_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error processing image {filename}: {e}")
            
            # Send error result
            self.results_producer.send_analysis_result(
                request_id=request_id,
                results=[],
                user_id=user_id,
                error=str(e)
            )
    
    def start_processing(self):
        """Start the image processing service."""
        print("🚀 Starting CLIP Image Processor Service")
        print("🎧 Waiting for images to process...")
        self.running = True
        
        try:
            # Start consuming images from Kafka
            self.consumer.consume_images(self.process_image_message)
            
        except Exception as e:
            print(f"❌ Error in processing service: {e}")
        finally:
            self.cleanup()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up resources...")
        if self.consumer:
            self.consumer.close()
        if self.results_producer:
            self.results_producer.producer.close()

def main():
    """Main function to run the processor service."""
    print("="*60)
    print("🎯 CLIP Image Processor Service")
    print("="*60)
    
    # Create and start the processor
    processor = CLIPImageProcessor()
    processor.start_processing()

if __name__ == "__main__":
    main()
