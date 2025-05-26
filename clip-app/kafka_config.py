# Kafka Configuration for CLIP Real-time Image Analysis

import os
from kafka import KafkaProducer, KafkaConsumer
import json
import base64
import uuid
import time
from datetime import datetime

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
IMAGE_UPLOAD_TOPIC = 'image-uploads'
ANALYSIS_RESULTS_TOPIC = 'analysis-results'
SYSTEM_STATUS_TOPIC = 'system-status'

# Kafka Producer Configuration
PRODUCER_CONFIG = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,
    'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
    'key_serializer': lambda k: k.encode('utf-8') if k else None,
    'acks': 'all',  # Wait for all replicas to acknowledge
    'retries': 3,
    'retry_backoff_ms': 300,
    'request_timeout_ms': 30000,
    'max_request_size': 10485760,  # 10MB to handle large images
    'buffer_memory': 33554432,     # 32MB buffer
}

# Kafka Consumer Configuration
CONSUMER_CONFIG = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,
    'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
    'key_deserializer': lambda k: k.decode('utf-8') if k else None,
    'auto_offset_reset': 'latest',
    'enable_auto_commit': True,
    'group_id': None,  # Will be set per consumer
    'max_partition_fetch_bytes': 10485760,  # 10MB to handle large messages
    'fetch_max_bytes': 52428800,  # 50MB total fetch size
}

class KafkaImageProducer:
    """Kafka producer for sending image analysis requests."""
    
    def __init__(self):
        self.producer = None
        self.connect()
    
    def connect(self):
        """Connect to Kafka with retry logic."""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(**PRODUCER_CONFIG)
                print(f"✅ Kafka producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
                return
            except Exception as e:
                retry_count += 1
                print(f"❌ Failed to connect to Kafka (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    raise Exception(f"Failed to connect to Kafka after {max_retries} attempts")
    
    def send_image_for_analysis(self, image_data, filename, user_id=None):
        """Send image data to Kafka for analysis."""
        try:
            # Generate unique request ID
            request_id = str(uuid.uuid4())
            
            # Convert image to base64 for JSON serialization
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create message payload
            message = {
                'request_id': request_id,
                'user_id': user_id or 'anonymous',
                'filename': filename,
                'image_data': image_base64,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Send to Kafka
            future = self.producer.send(
                IMAGE_UPLOAD_TOPIC,
                key=request_id,
                value=message
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            print(f"✅ Image sent to Kafka: topic={record_metadata.topic}, "
                  f"partition={record_metadata.partition}, offset={record_metadata.offset}")
            
            return request_id
            
        except Exception as e:
            print(f"❌ Error sending image to Kafka: {e}")
            raise
    
    def send_status_update(self, message_type, data):
        """Send system status updates."""
        try:
            status_message = {
                'type': message_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.producer.send(
                SYSTEM_STATUS_TOPIC,
                value=status_message
            )
            
        except Exception as e:
            print(f"❌ Error sending status update: {e}")
    
    def close(self):
        """Close the producer connection."""
        if self.producer:
            self.producer.close()

class KafkaImageConsumer:
    """Kafka consumer for processing image analysis requests."""
    
    def __init__(self, group_id='clip-processors'):
        self.group_id = group_id
        self.consumer = None
        self.connect()
    
    def connect(self):
        """Connect to Kafka consumer."""
        try:
            config = CONSUMER_CONFIG.copy()
            config['group_id'] = self.group_id
            
            self.consumer = KafkaConsumer(
                IMAGE_UPLOAD_TOPIC,
                **config
            )
            print(f"✅ Kafka consumer connected with group_id: {self.group_id}")
            
        except Exception as e:
            print(f"❌ Failed to connect consumer: {e}")
            raise
    
    def consume_images(self, callback_function):
        """Consume images from Kafka and process them."""
        print(f"🎧 Starting to consume images from topic: {IMAGE_UPLOAD_TOPIC}")
        
        try:
            for message in self.consumer:
                try:
                    image_data = message.value
                    print(f"📨 Received image for processing: {image_data['request_id']}")
                    
                    # Call the callback function to process the image
                    callback_function(image_data)
                    
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("🛑 Consumer stopped by user")
        except Exception as e:
            print(f"❌ Consumer error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close the consumer connection."""
        if self.consumer:
            self.consumer.close()

class KafkaResultsProducer:
    """Producer for sending analysis results."""
    
    def __init__(self):
        self.producer = KafkaImageProducer()
    
    def send_analysis_result(self, request_id, results, user_id, processing_time=None, error=None):
        """Send analysis results back to Kafka."""
        try:
            result_message = {
                'request_id': request_id,
                'user_id': user_id,
                'results': results,
                'processing_time': processing_time,
                'error': error,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed' if not error else 'failed'
            }
            
            future = self.producer.producer.send(
                ANALYSIS_RESULTS_TOPIC,
                key=request_id,
                value=result_message
            )
            
            record_metadata = future.get(timeout=10)
            print(f"✅ Analysis result sent: {request_id}")
            
        except Exception as e:
            print(f"❌ Error sending analysis result: {e}")
            raise

class KafkaResultsConsumer:
    """Consumer for receiving analysis results."""
    
    def __init__(self, group_id='result-consumers'):
        self.group_id = group_id
        self.consumer = None
        self.connect()
    
    def connect(self):
        """Connect to Kafka consumer for results."""
        try:
            config = CONSUMER_CONFIG.copy()
            config['group_id'] = self.group_id
            
            self.consumer = KafkaConsumer(
                ANALYSIS_RESULTS_TOPIC,
                **config
            )
            print(f"✅ Results consumer connected with group_id: {self.group_id}")
            
        except Exception as e:
            print(f"❌ Failed to connect results consumer: {e}")
            raise
    
    def consume_results(self, callback_function):
        """Consume analysis results from Kafka."""
        print(f"🎧 Starting to consume results from topic: {ANALYSIS_RESULTS_TOPIC}")
        
        try:
            for message in self.consumer:
                try:
                    result_data = message.value
                    print(f"📨 Received analysis result: {result_data['request_id']}")
                    
                    # Call the callback function to handle the result
                    callback_function(result_data)
                    
                except Exception as e:
                    print(f"❌ Error processing result: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("🛑 Results consumer stopped by user")
        except Exception as e:
            print(f"❌ Results consumer error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close the consumer connection."""
        if self.consumer:
            self.consumer.close()
