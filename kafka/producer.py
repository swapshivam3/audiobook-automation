from kafka import KafkaProducer
import json
import config

producer = KafkaProducer(
    bootstrap_servers=config.KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def publish_event(topic, data):
    """Send a message to a Kafka topic."""
    producer.send(topic, data)
    producer.flush()
