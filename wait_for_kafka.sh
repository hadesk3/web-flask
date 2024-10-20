#!/bin/bash
# Chờ Kafka sẵn sàng trên cổng 9092
while ! nc -z kafka 9092; do
  echo "Đợi Kafka khởi động..."
  sleep 5
done
echo "Kafka đã sẵn sàng!"
exec "$@"
