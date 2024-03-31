#!/usr/bin/env bash

docker exec kafka_aml \
    /opt/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic financial-transaction \
    --from-beginning
