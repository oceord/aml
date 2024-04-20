import csv
import json
import os
from pathlib import Path
from time import sleep

from kafka import KafkaProducer

SCRIPT_DIR = Path(__file__).parent

KAFKA_SERVER = os.environ.get("KAFKA_SERVER", "localhost:9092")
DATA_DIR = Path(os.environ.get("DATA_DIR", SCRIPT_DIR.parent.parent / "data" / "work"))
TOPIC = os.environ.get("TOPIC", "financial-transaction")
SEC_BETWEEN_MSGS = int(os.environ.get("SEC_BETWEEN_MSGS", 0))


def produce_events():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    with get_csv_file().open() as file:
        fieldnames = [
            "Timestamp",
            "From Bank",
            "From Account",
            "To Bank",
            "To Account",
            "Amount Received",
            "Receiving Currency",
            "Amount Paid",
            "Payment Currency",
            "Payment Format",
            "Is Laundering",
        ]
        reader = csv.DictReader(file, delimiter=",", fieldnames=fieldnames)
        next(reader, None)
        for row in reader:
            produce_event(producer, row)


def produce_event(producer, row):
    producer.send(topic=TOPIC, value=row)
    producer.flush()
    if SEC_BETWEEN_MSGS:
        sleep(SEC_BETWEEN_MSGS)


def get_csv_file():
    for file in DATA_DIR.iterdir():
        if file.is_file() and str(file).endswith(".csv"):
            return file
    return None


if __name__ == "__main__":
    produce_events()
