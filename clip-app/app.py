# Import SSL fix first, before any other imports
try:
    import ssl_fix
    print("SSL certificate verification disabled - Running in insecure mode")
except ImportError:
    print("WARNING: SSL fix module not found, continuing with default SSL settings")

import streamlit as st
import torch
from PIL import Image
import io
import time

# Import monitoring metrics
try:
    import metrics
    print("Metrics initialization successful - Prometheus monitoring enabled")
except ImportError as e:
    print(f"WARNING: Metrics module not found, continuing without monitoring: {e}")

# Fix for "no running event loop" error
import nest_asyncio
nest_asyncio.apply()

# Try to import CLIP-specific classes with better error handling
try:
    from transformers import CLIPProcessor, CLIPModel
    print("Successfully imported CLIP modules")
except ImportError as e:
    st.error(f"Error importing CLIP modules: {str(e)}")
    st.info("This might be caused by an incompatible transformers version. Make sure you're using transformers>=4.30.0")
    import sys
    print(f"Python version: {sys.version}")
    print(f"Error importing CLIP modules: {str(e)}")
    # Don't stop the app here, let it fail more gracefully
except Exception as e:
    st.error(f"Unexpected error importing CLIP modules: {str(e)}")
    if "SSL" in str(e) or "certificate" in str(e).lower():
        st.info("SSL certificate error detected. Trying to apply SSL certificate fix...")
        try:
            import ssl_fix
            # Try importing again after SSL fix
            from transformers import CLIPProcessor, CLIPModel
            st.success("Successfully imported CLIP modules after SSL fix")
        except Exception as e2:
            st.error(f"Still having issues after SSL fix: {str(e2)}")
    # Don't stop the app here, let it fail more gracefully
    
# Set page configuration
st.set_page_config(
    page_title="Image Analysis with CLIP",
    page_icon="🖼️",
    layout="wide"
)

@st.cache_resource
def load_model():
    """Load the CLIP model and processor."""
    import os
    try:
        # Check for environment variable that indicates we're running on Render
        is_render = os.environ.get('RENDER', '') == 'true'
        
        # Get absolute paths to model directories
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "models", "clip-model")
        processor_path = os.path.join(base_dir, "models", "clip-processor")
        
        # Create directories if they don't exist
        os.makedirs(model_path, exist_ok=True)
        os.makedirs(processor_path, exist_ok=True)
        
        # Download models from Hugging Face with SSL verification disabled
        model_id = "openai/clip-vit-base-patch32"
        st.info(f"Downloading model and processor from {model_id} with SSL verification disabled")
        
        # Explicitly disable SSL verification for Hugging Face
        import os
        os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'
        
        # Force no SSL verification in transformers
        model = CLIPModel.from_pretrained(model_id, trust_remote_code=True, 
                                         use_auth_token=False, 
                                         local_files_only=False,
                                         force_download=True)
        
        processor = CLIPProcessor.from_pretrained(model_id, trust_remote_code=True,
                                                use_auth_token=False,
                                                local_files_only=False,
                                                force_download=True)
        
        # Save models to local directories for future use
        try:
            os.makedirs(model_path, exist_ok=True)
            os.makedirs(processor_path, exist_ok=True)
            model.save_pretrained(model_path)
            processor.save_pretrained(processor_path)
            st.success("✅ Models downloaded and saved to local directory for future use")
        except Exception as e:
            st.warning(f"Models downloaded but could not save locally: {str(e)}")
        
        return model, processor
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        st.info("SSL certificate errors should be bypassed now. If you're still seeing SSL errors, please check that ssl_fix.py is working properly.")
        # Print system information for debugging
        import sys
        st.code(f"Python version: {sys.version}\nCurrent directory: {os.getcwd()}\nDirectory contents: {os.listdir('.')}")
        if os.path.exists("models"):
            st.code(f"Models directory contents: {os.listdir('models')}")
        st.stop()

def analyze_image(image, model, processor):
    """Analyze image using CLIP model and return descriptions."""
    try:
        # Record analysis request if metrics available
        if 'metrics' in globals():
            metrics.ANALYSIS_REQUESTS.inc()
            
        start_time = None
        if 'metrics' in globals():
            start_time = time.time()
            
        # Common objects and scenes to check
        candidate_labels = [
            "a photo of a person", "a photo of a landscape", "a photo of an animal",
            "a photo of food", "a photo of a building", "a photo of a vehicle",
            "a photo of nature", "a photo of technology", "a photo of art",
            "a photo of sports", "a photo of water", "a photo of mountains",
            "a photo of a city", "a photo of a beach", "a photo of flowers",
            "a photo of a cat", "a photo of a dog", "a photo of a bird",
            "a photo of text", "a photo of clothing", "a photo of furniture"
        ]
        
        # Process the image and text
        inputs = processor(
            text=candidate_labels,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Get model predictions
        with torch.no_grad():
            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        # Get top 5 predictions
        top_probs, top_indices = torch.topk(probs[0], k=5)
        
        results = []
        for i, (prob, idx) in enumerate(zip(top_probs, top_indices)):
            label = candidate_labels[idx]
            confidence = prob.item() * 100
            results.append((label, confidence))
        
        # Record analysis duration if metrics available
        if 'metrics' in globals() and start_time is not None:
            duration = time.time() - start_time
            metrics.ANALYSIS_DURATION.observe(duration)
            
        return results
    except Exception as e:
        # Record error if metrics available
        if 'metrics' in globals():
            metrics.ANALYSIS_ERRORS.inc()
        st.error(f"Error analyzing image: {str(e)}")
        return [("Error analyzing image", 0.0)]

def main():
    """Main function to run the Streamlit app."""
    try:
        # Track user connection if metrics available
        if 'metrics' in globals():
            metrics.user_connected()
            
        st.title("Image Analysis with CLIP")
        st.write("Upload an image and the model will tell you what's in it!")
        
        # Load model
        with st.spinner("Loading CLIP model..."):
            model, processor = load_model()
        
        # Image upload
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        # Display and analyze image
        if uploaded_file is not None:
            try:
                # Record upload if metrics available
                if 'metrics' in globals():
                    metrics.record_upload()
                    
                col1, col2 = st.columns(2)
                
                # Load and display image
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                col1.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Analyze image
                with st.spinner("Analyzing image..."):
                    results = analyze_image(image, model, processor)
                
                # Display results
                col2.subheader("Analysis Results:")
                for label, confidence in results:
                    if confidence > 0:  # Only show valid results
                        col2.write(f"- {label[11:]}: {confidence:.2f}%")  # Remove "a photo of" prefix
                
                # Explanation of results
                st.info("The percentages indicate the model's confidence that the image contains the specified content.")
            except Exception as e:
                if 'metrics' in globals():
                    metrics.ANALYSIS_ERRORS.inc()
                st.error(f"Error processing image: {str(e)}")
    except Exception as e:
        if 'metrics' in globals():
            metrics.ANALYSIS_ERRORS.inc()
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please try reloading the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()
