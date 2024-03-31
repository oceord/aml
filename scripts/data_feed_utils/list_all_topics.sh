#!/usr/bin/env bash

docker exec kafka_aml \
    /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9092 \
    --list
