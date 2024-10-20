import json
from kafka import KafkaConsumer
"""
# Kết nối đến Kafka
consumer = KafkaConsumer(
    'order_events',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='order_event_group'
)

for message in consumer:
    order_event = json.loads(message.value)
    print(f"Received order event: {order_event}")
"""   
