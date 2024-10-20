from kafka import KafkaConsumer
import json
import os
from elasticsearch import Elasticsearch
es_url = os.environ.get("ELASTICSEARCH_URL", "http://es-container:9200")
es = Elasticsearch(es_url)
consumer = KafkaConsumer('user_activity',
                         bootstrap_servers='kafka:9092',
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for message in consumer:
    activity_data = message.value
    es.index(index='user-activities', body=activity_data)
