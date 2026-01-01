"""
Consumer Print
--------------
Consumes messages from Kafka and simply prints them to the console.

- Useful for debugging (to see what raw events look like).
- Shows Kafka concepts: partition, offset, key, value.
- Each run uses its own "group_id", so it keeps its own position in the log.
"""

"""
Consumer that listens to Kafka and writes events into Parquet files (Bronze layer).
"""

import os, json, sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.kafka_factory import get_kafka_consumer

load_dotenv()

TOPIC = os.getenv("KAFKA_TOPIC", "energuide-events")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
BRONZE_DIR = os.path.join("data", "bronze")
os.makedirs(BRONZE_DIR, exist_ok=True)

def main():
    consumer = get_kafka_consumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="parquet-writer",
        key_deserializer=lambda k: k.decode() if k else None,
        value_deserializer=lambda v: json.loads(v.decode()),
    )

    buffer = []
    batch_size = 200

    for msg in consumer:
        buffer.append(msg.value)

        if len(buffer) >= batch_size:
            df = pd.DataFrame(buffer)
            now = datetime.utcnow()
            path = os.path.join(
                BRONZE_DIR,
                f"year={now.year}/month={now.month:02d}/day={now.day:02d}/hour={now.hour:02d}"
            )
            os.makedirs(path, exist_ok=True)
            file = os.path.join(path, f"batch_{now.strftime('%Y%m%dT%H%M%S')}.parquet")
            df.to_parquet(file, index=False)
            print(f"[bronze] wrote {len(buffer)} rows → {file}")
            buffer = []  # reset

if __name__ == "__main__":
    main()
