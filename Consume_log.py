from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import os
# Kết nối với Elasticsearch
es_url = os.environ.get("ELASTICSEARCH_URL", "http://es-container:9200")
es = Elasticsearch(es_url)

# Tạo Kafka consumer
consumer = KafkaConsumer(
    'logs',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Gửi log vào Elasticsearch
for message in consumer:
    log_data = message.value
    es.index(index='logs',body=log_data)