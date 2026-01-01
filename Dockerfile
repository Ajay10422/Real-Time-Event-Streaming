# Dockerfile
# All-in-one container for Real-Time ML Pipeline
# Includes Python services and Redpanda (Kafka)

FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including Java for Redpanda alternative
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    curl \
    procps \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data /app/data/bronze /app/data/silver

# Make startup script executable
RUN chmod +x start_all.sh 2>/dev/null || true

# Expose the port for Streamlit
EXPOSE 8501

# Default command runs the startup script
CMD ["bash", "start_all.sh"]