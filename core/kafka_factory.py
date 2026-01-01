"""
Kafka Factory - automatically selects real or mock Kafka based on environment
"""
import os
import socket


def can_connect_to_kafka(bootstrap_servers: str) -> bool:
    """Check if we can connect to Kafka broker"""
    try:
        host, port = bootstrap_servers.split(':')
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_kafka_producer(bootstrap_servers: str, **kwargs):
    """Get a Kafka producer (real or mock based on availability)"""
    use_mock = os.getenv('USE_MOCK_KAFKA', 'false').lower() == 'true'

    if not use_mock and can_connect_to_kafka(bootstrap_servers):
        print(f"[kafka-factory] Using real Kafka at {bootstrap_servers}")
        from kafka import KafkaProducer
        return KafkaProducer(bootstrap_servers=bootstrap_servers, **kwargs)
    else:
        print(f"[kafka-factory] Using mock Kafka (real Kafka not available at {bootstrap_servers})")
        from core.mock_kafka import MockKafkaProducer
        return MockKafkaProducer(bootstrap_servers=bootstrap_servers, **kwargs)


def get_kafka_consumer(*topics, bootstrap_servers: str, **kwargs):
    """Get a Kafka consumer (real or mock based on availability)"""
    use_mock = os.getenv('USE_MOCK_KAFKA', 'false').lower() == 'true'

    if not use_mock and can_connect_to_kafka(bootstrap_servers):
        print(f"[kafka-factory] Using real Kafka at {bootstrap_servers}")
        from kafka import KafkaConsumer
        return KafkaConsumer(*topics, bootstrap_servers=bootstrap_servers, **kwargs)
    else:
        print(f"[kafka-factory] Using mock Kafka (real Kafka not available at {bootstrap_servers})")
        from core.mock_kafka import MockKafkaConsumer
        return MockKafkaConsumer(*topics, bootstrap_servers=bootstrap_servers, **kwargs)
