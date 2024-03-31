#!/usr/bin/env bash

docker exec kafka_aml \
    /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9092 \
    --create --topic financial-transaction \
    --partitions 1 \
    --replication-factor 1
