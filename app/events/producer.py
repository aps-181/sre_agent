import json
import logging
from aiokafka import AIOKafkaProducer

BOOTSTRAP_SERVERS = "localhost:19092"


class AlertProducer:
    def __init__(self, bootstrap_servers: str = BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_alert(self, topic: str, payload: dict):
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")
        await self.producer.send_and_wait(topic, payload)
        logging.info(
            f"[Producer] Alert published to topic '{topic}': {payload.get('service_name')}"
        )
