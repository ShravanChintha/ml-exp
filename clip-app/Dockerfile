FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    ca-certificates \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create models directory structure
RUN mkdir -p /app/models/clip-model /app/models/clip-processor

# Copy application code
COPY app.py .
COPY ssl_fix.py .
COPY README.md .

# Model directory will be mounted as a volume in docker-compose.yml
# In this online mode, models will be downloaded if not available

# Update certificates
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade certifi

# Create an insecure pip configuration that bypasses SSL verification
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "trusted-host = pypi.python.org files.pythonhosted.org pypi.org cdn-lfs.huggingface.co" >> /root/.pip/pip.conf

# Disable SSL verification for Python
ENV PYTHONHTTPSVERIFY=0

# Expose port for Streamlit (Render will set PORT env var)
EXPOSE 8501
ENV PORT=8501

# The command will be overridden by docker-compose.yml or render.yaml
# But provide a default for standalone docker run
CMD streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
