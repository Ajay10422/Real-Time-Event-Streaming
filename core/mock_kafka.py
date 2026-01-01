"""
Mock Kafka implementation for local/demo environments
This allows the pipeline to run without a real Kafka broker.
"""
import json
import threading
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional


class MockKafkaProducer:
    """Mock Kafka Producer that writes to an in-memory queue"""

    def __init__(self, bootstrap_servers, **kwargs):
        self.bootstrap_servers = bootstrap_servers
        self.closed = False

    def send(self, topic: str, key=None, value=None):
        """Send a message to the mock broker"""
        if self.closed:
            raise RuntimeError("Producer is closed")
        MockKafkaBroker.add_message(topic, key, value)
        return MockFuture()

    def flush(self):
        """Mock flush - does nothing as messages are immediately available"""
        pass

    def close(self):
        """Close the producer"""
        self.closed = True


class MockKafkaConsumer:
    """Mock Kafka Consumer that reads from an in-memory queue"""

    def __init__(self, *topics, bootstrap_servers, group_id=None,
                 auto_offset_reset='earliest', **kwargs):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id or 'default-group'
        self.auto_offset_reset = auto_offset_reset
        self.closed = False
        self._offset = defaultdict(int)

    def __iter__(self):
        return self

    def __next__(self):
        """Get next message from the queue"""
        if self.closed:
            raise StopIteration

        # Try to get messages from all subscribed topics
        for topic in self.topics:
            messages = MockKafkaBroker.get_messages(
                topic,
                self.group_id,
                self._offset[topic]
            )
            if messages:
                msg = messages[0]
                self._offset[topic] += 1
                return MockMessage(msg['key'], msg['value'], topic)

        # No messages available, sleep a bit
        time.sleep(0.5)
        return self.__next__()

    def close(self):
        """Close the consumer"""
        self.closed = True


class MockMessage:
    """Mock Kafka Message"""

    def __init__(self, key, value, topic):
        self.key = key
        self.value = value
        self.topic = topic


class MockFuture:
    """Mock Future for send operation"""

    def get(self, timeout=None):
        return None


class MockKafkaBroker:
    """In-memory message broker (singleton)"""

    _messages = defaultdict(list)
    _lock = threading.Lock()

    @classmethod
    def add_message(cls, topic: str, key: Any, value: Any):
        """Add a message to the topic"""
        with cls._lock:
            cls._messages[topic].append({
                'key': key,
                'value': value,
                'timestamp': time.time()
            })

    @classmethod
    def get_messages(cls, topic: str, group_id: str, offset: int) -> List[Dict]:
        """Get messages from a topic starting at offset"""
        with cls._lock:
            all_msgs = cls._messages.get(topic, [])
            if offset < len(all_msgs):
                return [all_msgs[offset]]
            return []

    @classmethod
    def reset(cls):
        """Clear all messages (for testing)"""
        with cls._lock:
            cls._messages.clear()
