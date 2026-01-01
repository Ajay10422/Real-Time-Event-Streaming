#!/bin/bash
# Startup script to run all pipeline components in a single Render service

echo "========================================="
echo "Starting Real-Time ML Pipeline"
echo "========================================="

# Set default environment variables
export PYTHONUNBUFFERED=1
export KAFKA_TOPIC=${KAFKA_TOPIC:-energuide-events}
export KAFKA_BOOTSTRAP=${KAFKA_BOOTSTRAP:-localhost:9092}
export USE_MOCK_KAFKA=${USE_MOCK_KAFKA:-true}

echo "Environment:"
echo "  - KAFKA_BOOTSTRAP: $KAFKA_BOOTSTRAP"
echo "  - KAFKA_TOPIC: $KAFKA_TOPIC"
echo "  - USE_MOCK_KAFKA: $USE_MOCK_KAFKA"
echo "  - PORT: ${PORT:-8501}"
echo "========================================="

# Create necessary directories
mkdir -p /app/data/bronze /app/data/silver
echo "✓ Created data directories"

# Start Kafka producer in background
echo "Starting producer..."
python ingestion/producer.py > /tmp/producer.log 2>&1 &
PRODUCER_PID=$!
echo "✓ Producer started (PID: $PRODUCER_PID)"

# Give producer a moment to start
sleep 2

# Start bronze consumer in background
echo "Starting bronze consumer..."
python transform/consumer_to_parquet.py > /tmp/bronze.log 2>&1 &
BRONZE_PID=$!
echo "✓ Bronze consumer started (PID: $BRONZE_PID)"

# Start silver consumer in background
echo "Starting silver consumer..."
python transform/consumer_to_silver.py > /tmp/silver.log 2>&1 &
SILVER_PID=$!
echo "✓ Silver consumer started (PID: $SILVER_PID)"

# Start trainer in background
echo "Starting trainer..."
python transform/consumer_trainer.py > /tmp/trainer.log 2>&1 &
TRAINER_PID=$!
echo "✓ Trainer started (PID: $TRAINER_PID)"

# Give everything a moment to initialize
sleep 3

echo "========================================="
echo "All background services started!"
echo "Starting Streamlit dashboard..."
echo "========================================="

# Function to handle shutdown
shutdown() {
    echo ""
    echo "========================================="
    echo "Shutting down all services..."
    echo "========================================="
    kill $PRODUCER_PID $BRONZE_PID $SILVER_PID $TRAINER_PID 2>/dev/null
    echo "✓ All services stopped"
    exit 0
}

# Trap SIGTERM and SIGINT for graceful shutdown
trap shutdown SIGTERM SIGINT

# Start Streamlit dashboard in foreground
streamlit run dashboard/training_monitor.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.runOnSave=false \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false

# If streamlit exits, cleanup
shutdown
