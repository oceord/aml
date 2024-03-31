#!/usr/bin/env bash

echo "foo" |
    docker exec -i kafka_aml \
        /opt/kafka/bin/kafka-console-producer.sh \
        --broker-list localhost:9092 \
        --topic financial-transaction \
        -
