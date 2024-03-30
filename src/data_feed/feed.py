import csv
import json
from pathlib import Path
from time import sleep

from kafka import KafkaProducer

TOPIC = "financial-transaction"
KAFKA_SERVER = "localhost:9092"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data" / "work"
SEC_BETWEEN_MSGS = 5


def produce_events():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    with get_csv_file().open() as file:
        reader = csv.DictReader(file, delimiter=",")
        for row in reader:
            produce_event(producer, row)


def produce_event(producer, row):
    producer.send(topic=TOPIC, value=row)
    producer.flush()
    sleep(SEC_BETWEEN_MSGS)


def get_csv_file():
    for file in DATA_DIR.iterdir():
        if file.is_file() and str(file).endswith(".csv"):
            return file
    return None


if __name__ == "__main__":
    produce_events()
